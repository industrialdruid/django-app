from django.contrib.auth.models import User
from django.db import models


def profile_images_directory_path(instance: "Profile", filename: str) -> str:
    return "profiles/user_{pk}/images/{filename}".format(
        pk=instance.user.pk,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=profile_images_directory_path, blank=True)

