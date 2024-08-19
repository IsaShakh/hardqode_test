from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from courses.models import Course

class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        verbose_name='Баланс',
    )

    def save(self, *args, **kwargs):
        if self.balance < 0:
            raise ValidationError("Баланс не может быть меньше 0.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        verbose_name='Пользователь')
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
    )
    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Начало подписки'
    )
    end_date = models.DateTimeField(
        verbose_name='Дата окончания подписки'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)

    def deactivate(self):
        """Деактивировать подписку."""
        self.is_active = False
        self.save()

