from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default_profile.png"
    )

    cover_picture = models.ImageField(
        upload_to="cover_pictures/",
        default="cover_pictures/default_cover.jpg"
    )

    bio = models.TextField(blank=True)

    location = models.CharField(
        max_length=100,
        blank=True
    )

    college = models.CharField(
        max_length=100,
        blank=True
    )

    profession = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(blank=True)

    def __str__(self):
        return self.user.username