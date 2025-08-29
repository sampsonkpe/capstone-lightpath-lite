from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        # For development / debugging
        print(f"New user created: {instance.email}")

        # Only send email if DEBUG is False (production)
        if not settings.DEBUG:
            send_mail(
                'Welcome to LightPath Lite',
                'Thank you for registering with LightPath Lite.',
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )