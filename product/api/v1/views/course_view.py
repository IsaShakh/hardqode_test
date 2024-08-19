from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_queryset(self):
        user = self.request.user
        return Course.objects.annotate(lessons_count = Count('lesson').filter(is_available=True).exclude(
            id__in=Subscription.objects.filter(user=user, is_active=True).values_list('course_id', flat=True)))

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer
    
    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        course = self.get_object()
        user = request.user

        if user.balance.balance < course.price:
            return Response(
                {"detail": "Недостаточно бонусов для оплаты курса."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.balance.balance -= course.price
        user.balance.save()

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={'is_active': True}
        )

        if not created:
            return Response(
                {"detail": "Вы уже подписаны на этот курс."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.assign_user_to_group(course, user)

        return Response(
            data=data,
            status=status.HTTP_201_CREATED
        )
    
    def assign_user_to_group(self, course, user):
        """Распределение пользователя в одну из 10 групп курса."""
        max_students_per_group = 30
        groups = Group.objects.filter(course=course)

        if groups.count() < 10:
            for i in range(10 - groups.count()):
                Group.objects.create(course=course, name=f"Группа {groups.count() + i + 1}")

        min_group = min(groups, key=lambda g: g.subscription_set.count())

        if min_group.subscription_set.count() < max_students_per_group:
            subscription = Subscription.objects.get(user=user, course=course)
            subscription.group = min_group
            subscription.save()
        else:
            new_group = Group.objects.create(course=course, name=f"Группа {groups.count() + 1}")
            subscription = Subscription.objects.get(user=user, course=course)
            subscription.group = new_group
            subscription.save()
