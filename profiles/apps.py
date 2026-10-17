from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from django.contrib.auth import get_user_model
        from .models import Profile

        User = get_user_model()

        @receiver(post_save, sender=User, dispatch_uid="profiles_create_user_profile")
        def create_user_profile(sender, instance, created, **kwargs):
            if created:
                Profile.objects.get_or_create(user=instance)
