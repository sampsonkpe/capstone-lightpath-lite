from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        # Log user creation
        logger.info(f"New user created: {instance.email}")

        # Only send email if DEBUG is False (production)
        if not settings.DEBUG:
            try:
                send_mail(
                    subject='Welcome to LightPath Lite',
                    message='Thank you for registering with LightPath Lite.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=False,
                )
                logger.info(f"Welcome email sent to: {instance.email}")
            except Exception as e:
                logger.error(f"Error sending welcome email to {instance.email}: {e}")