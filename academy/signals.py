from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment, Notification

@receiver(post_save, sender=Enrollment)
def notify_activation(sender, instance, created, **kwargs):
    # Si se yon modifikasyon (pa yon kreyasyon) epi is_active vin True
    if not created and instance.is_active:
        Notification.objects.create(
            user=instance.user,
            title="Kou Aktive! 🎉",
            message=f"Peman ou pou kou '{instance.course.title}' la valide. Ou ka kòmanse aprann kounye a!",
            url=f"/courses/{instance.course.id}/" # URL Dashboard kou a
        )