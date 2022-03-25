from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Donate


@receiver(post_save, sender=Donate)
@receiver(post_delete, sender=Donate)
def after_donation_change(sender, instance, **kwargs):
    instance.project.update_close_status()
