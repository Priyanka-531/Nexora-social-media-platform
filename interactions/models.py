from django.db import models
from django.contrib.auth.models import User

from posts.models import Post


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.TextField(
        max_length=500
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"


class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow"
            )
        ]

    def __str__(self):

        return (
            f"{self.follower.username} "
            f"→ "
            f"{self.following.username}"
        )


class FollowRequest(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_follow_requests"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_follow_requests"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_follow_request"
            )
        ]

    def __str__(self):

        return f"{self.sender.username} → {self.receiver.username} ({self.status})"


class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("follow_request", "Follow Request"),
        ("follow_accept", "Follow Request Accepted"),
        ("new_follower", "New Follower"),
        ("like", "Like"),
        ("comment", "Comment"),
        ("mention", "Mention"),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return f"Notification for {self.recipient.username}: {self.notification_type} from {self.sender.username}"
