import re
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from posts.models import Post
from .models import Comment, Follow, FollowRequest, Notification


class NotificationService:
    """
    Business Logic Service for System Notifications.
    Handles notification creation, deduplication, retrieval, marking as read, and redirection.
    """

    @staticmethod
    def create_notification(recipient, sender, notification_type, post=None):
        """
        Creates a new Notification object if recipient != sender and prevents unnecessary duplicates.
        """
        if recipient == sender:
            return None

        # Deduplication checks
        if notification_type == "like" and post:
            if Notification.objects.filter(recipient=recipient, sender=sender, notification_type="like", post=post).exists():
                return None

        if notification_type == "follow_request":
            if Notification.objects.filter(recipient=recipient, sender=sender, notification_type="follow_request", is_read=False).exists():
                return None

        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            post=post
        )
        return notification

    @staticmethod
    def parse_and_notify_mentions(sender, text, post):
        """
        Extracts @username mentions from text and sends mention notifications.
        """
        if not text or "@" not in text:
            return

        usernames = set(re.findall(r'@(\w+)', text))
        for username in usernames:
            try:
                mentioned_user = User.objects.get(username=username)
                NotificationService.create_notification(
                    recipient=mentioned_user,
                    sender=sender,
                    notification_type="mention",
                    post=post
                )
            except User.DoesNotExist:
                continue

    @staticmethod
    def get_user_notifications(user, filter_type=None):
        """
        Retrieves notifications list for user.
        """
        qs = Notification.objects.filter(recipient=user).select_related("sender__profile", "post", "post__author", "post__author__profile")
        if filter_type == "unread":
            qs = qs.filter(is_read=False)
        return qs

    @staticmethod
    def mark_as_read(user, notification_id):
        """
        Marks a specific notification as read.
        """
        try:
            notif = Notification.objects.get(id=notification_id, recipient=user)
            notif.is_read = True
            notif.save()
            unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
            return True, unread_count
        except Notification.DoesNotExist:
            return False, 0

    @staticmethod
    def mark_all_as_read(user):
        """
        Marks all notifications for user as read.
        """
        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return True, 0

    @staticmethod
    def get_target_url(notification):
        """
        Returns destination URL based on notification_type and linked post/sender.
        """
        ntype = notification.notification_type
        if ntype == "follow_request":
            return "/requests/"
        elif ntype in ["follow_accept", "new_follower"]:
            return f"/profile/{notification.sender.username}/"
        elif ntype in ["like", "comment", "mention"] and notification.post:
            return f"/profile/{notification.post.author.username}/#post-{notification.post.id}"
        return f"/profile/{notification.sender.username}/"


class InteractionService:
    """
    Business Logic Service for User Interactions (Comments, Follows, and Follow Requests).
    """

    @staticmethod
    def add_comment(post_id, user, text):
        """
        Validates comment input, creates comment record, and triggers notifications.
        """
        text = text.strip() if text else ""

        if not text:
            return False, {"message": "Comment cannot be empty."}, 400

        if len(text) > 500:
            return False, {"message": "Comment is too long."}, 400

        post = get_object_or_404(Post, id=post_id)

        comment = Comment.objects.create(
            post=post,
            user=user,
            text=text
        )

        # Trigger comment notification
        NotificationService.create_notification(
            recipient=post.author,
            sender=user,
            notification_type="comment",
            post=post
        )

        # Trigger @mention notifications if present
        NotificationService.parse_and_notify_mentions(user, text, post)

        return True, {
            "comment": {
                "id": comment.id,
                "username": comment.user.username,
                "text": comment.text,
            },
            "comment_count": post.comments.count()
        }, 200

    @staticmethod
    def delete_comment(comment_id, user):
        """
        Deletes a comment if the user is the original author.
        """
        comment = get_object_or_404(Comment, id=comment_id)

        if comment.user != user:
            return False, {"message": "You cannot delete this comment."}, 403

        post = comment.post
        comment.delete()

        return True, {
            "comment_count": post.comments.count()
        }, 200

    @staticmethod
    def toggle_follow(follower_user, target_username):
        """
        Handles follow/unfollow actions between follower_user and target_user.
        Automatically establishes Follow relationship immediately upon clicking Follow with notification.
        Returns (success, status_str, is_following, is_requested, target_followers_count, target_following_count, follower_following_count, message).
        status_str: 'following' or 'none'
        """
        target_user = get_object_or_404(User, username=target_username)

        if follower_user == target_user:
            return False, "none", False, False, 0, 0, 0, "You cannot follow yourself."

        # Case 1: Already Following -> Unfollow
        follow = Follow.objects.filter(
            follower=follower_user,
            following=target_user
        ).first()

        if follow:
            follow.delete()
            FollowRequest.objects.filter(sender=follower_user, receiver=target_user).delete()
            status_str = "none"
            is_following = False
            is_requested = False
            message = f"You unfollowed @{target_user.username}."

        else:
            # Case 2: Clicked Follow -> Automatically establish Follow relationship immediately!
            Follow.objects.get_or_create(
                follower=follower_user,
                following=target_user
            )

            req, _ = FollowRequest.objects.get_or_create(
                sender=follower_user,
                receiver=target_user
            )
            req.status = "accepted"
            req.save()

            NotificationService.create_notification(
                recipient=target_user,
                sender=follower_user,
                notification_type="new_follower"
            )

            status_str = "following"
            is_following = True
            is_requested = False
            message = f"You are now following @{target_user.username}."

        target_followers_count = Follow.objects.filter(following=target_user).count()
        target_following_count = Follow.objects.filter(follower=target_user).count()
        follower_following_count = Follow.objects.filter(follower=follower_user).count()

        return True, status_str, is_following, is_requested, target_followers_count, target_following_count, follower_following_count, message

    @staticmethod
    def seed_welcome_interactions(user):
        """
        Seeds initial realistic follow requests and notifications for new/logged users
        so every logged user has follow requests and notifications to test and interact with.
        """
        if not user or not user.is_authenticated:
            return

        demo_usernames = ["nexora_creator", "design_with_riya", "tech_aarav", "travel_with_anaya", "code_with_rohan", "photography_meera"]
        demo_users = list(User.objects.filter(username__in=demo_usernames).exclude(id=user.id))

        if not demo_users:
            return

        # 1. Seed pending follow requests if user has fewer than 2 pending requests
        pending_count = FollowRequest.objects.filter(receiver=user, status="pending").count()
        if pending_count < 2:
            for sender in demo_users[:3]:
                if not Follow.objects.filter(follower=sender, following=user).exists():
                    req, created = FollowRequest.objects.get_or_create(
                        sender=sender,
                        receiver=user,
                        defaults={"status": "pending"}
                    )
                    if created or req.status == "pending":
                        NotificationService.create_notification(
                            recipient=user,
                            sender=sender,
                            notification_type="follow_request"
                        )

        # 2. Seed a new follower notification if notifications list is sparse
        if Notification.objects.filter(recipient=user).count() < 3 and len(demo_users) > 3:
            follower_sender = demo_users[3]
            Follow.objects.get_or_create(follower=follower_sender, following=user)
            NotificationService.create_notification(
                recipient=user,
                sender=follower_sender,
                notification_type="new_follower"
            )

    @staticmethod
    def get_pending_requests(user):
        """
        Retrieves all pending follow requests received by user.
        """
        return FollowRequest.objects.filter(
            receiver=user,
            status="pending"
        ).select_related("sender__profile").order_by("-created_at")

    @staticmethod
    def accept_follow_request(receiver_user, request_id):
        """
        Accepts a pending follow request:
        - Creates Follow relationship
        - Updates request status to 'accepted'
        - Creates follow_accept and new_follower notifications for sender
        Returns (success, data, status_code).
        """
        req = get_object_or_404(FollowRequest, id=request_id, receiver=receiver_user)

        if req.status != "pending":
            return False, {"message": "Follow request is no longer pending."}, 400

        # Create Follow relationship
        Follow.objects.get_or_create(
            follower=req.sender,
            following=req.receiver
        )

        req.status = "accepted"
        req.save()

        # Create notifications
        NotificationService.create_notification(
            recipient=req.sender,
            sender=req.receiver,
            notification_type="follow_accept"
        )
        NotificationService.create_notification(
            recipient=req.receiver,
            sender=req.sender,
            notification_type="new_follower"
        )

        pending_count = FollowRequest.objects.filter(receiver=receiver_user, status="pending").count()

        return True, {
            "message": f"Accepted @{req.sender.username}'s follow request.",
            "sender_username": req.sender.username,
            "pending_count": pending_count
        }, 200

    @staticmethod
    def reject_follow_request(receiver_user, request_id):
        """
        Rejects a pending follow request:
        - Updates request status to 'rejected'
        - Does NOT create Follow relationship
        Returns (success, data, status_code).
        """
        req = get_object_or_404(FollowRequest, id=request_id, receiver=receiver_user)

        if req.status != "pending":
            return False, {"message": "Follow request is no longer pending."}, 400

        req.status = "rejected"
        req.save()

        pending_count = FollowRequest.objects.filter(receiver=receiver_user, status="pending").count()

        return True, {
            "message": f"Rejected @{req.sender.username}'s follow request.",
            "sender_username": req.sender.username,
            "pending_count": pending_count
        }, 200


