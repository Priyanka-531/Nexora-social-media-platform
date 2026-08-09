from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    image = models.ImageField(
        upload_to="posts/"
    )

    caption = models.TextField(
        max_length=1000
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank=True
    )

    saved_by = models.ManyToManyField(
        User,
        related_name="saved_posts",
        blank=True
    )

    def __str__(self):
        return (
            f"{self.author.username} - "
            f"{self.created_at.strftime('%d/%m/%Y')}"
        )


class Story(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stories"
    )
    image = models.ImageField(
        upload_to="stories/"
    )
    caption = models.TextField(
        max_length=500,
        blank=True,
        default=""
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Stories"

    def is_active(self):
        if not self.expires_at:
            return True
        return timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Story by @{self.author.username} ({self.id})"