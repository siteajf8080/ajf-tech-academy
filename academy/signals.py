from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment, Notification, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Enrollment)
def notify_activation(sender, instance, created, **kwargs):
    if not created and instance.is_active:
        Notification.objects.create(
            user=instance.user,
            title="Kou Aktive!",
            message=f"Peman ou pou kou '{instance.course.title}' la valide. Ou ka komanse aprann kounye a!",
            url=f"/course/{instance.course.id}/",
        )
