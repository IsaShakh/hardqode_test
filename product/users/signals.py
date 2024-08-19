from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Balance

@receiver(post_save, sender=CustomUser)
def create_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)