from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription
from .models import Group


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.
    """
    if created:
        course = instance.course
        groups = Group.objects.filter(course=course)

        if not groups.exists():
            group = Group.objects.create(course=course, name=f"Группа 1")
        else:
            group = min(groups, key=lambda g: g.subscription_set.count())
        instance.group = group
        instance.save()

