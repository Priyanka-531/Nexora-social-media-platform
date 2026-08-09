from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Post, Story
from .forms import PostForm


class PostService:
    """
    Business Logic Service for Posts and Media Content.
    Handles post creation, ownership verification, liking/unliking, and deletion.
    """

    @staticmethod
    def get_post_form(post_data=None, files_data=None):
        """
        Instantiates PostForm with optional request data.
        """
        if post_data is not None:
            return PostForm(post_data, files_data)
        return PostForm()

    @staticmethod
    def create_post(user, form):
        """
        Saves a new post with the given user as author and notifies mentioned users.
        """
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()

            from interactions.services import NotificationService
            NotificationService.parse_and_notify_mentions(user, post.caption, post)

            return post, True
        return None, False

    @staticmethod
    def toggle_like(user, post_id, force_like=False):
        """
        Toggles like status for a post by user. Returns (success, liked_status, likes_count).
        If force_like is True, ensures the post is liked without unliking.
        """
        post = get_object_or_404(Post, id=post_id)

        is_liked = post.likes.filter(id=user.id).exists()

        if force_like:
            if not is_liked:
                post.likes.add(user)
            liked = True
        else:
            if is_liked:
                post.likes.remove(user)
                liked = False
            else:
                post.likes.add(user)
                liked = True

        if liked:
            from interactions.services import NotificationService
            NotificationService.create_notification(
                recipient=post.author,
                sender=user,
                notification_type="like",
                post=post
            )

        likes_count = post.likes.count()
        return True, liked, likes_count

    @staticmethod
    def toggle_save(user, post_id):
        """
        Toggles bookmark/saved status for a post by user. Returns (success, saved_status).
        """
        post = get_object_or_404(Post, id=post_id)
        is_saved = post.saved_by.filter(id=user.id).exists()

        if is_saved:
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True

        return True, saved, f"Post {'saved' if saved else 'unsaved'} successfully."

    @staticmethod
    def delete_post(user, post_id):
        """
        Deletes a post if the user is authorized. Returns (success, message, status_code).
        """
        post = get_object_or_404(Post, id=post_id)

        if post.author != user:
            return False, "You cannot delete this post.", 403

        post.delete()
        return True, "Post deleted successfully.", 200


class StoryService:
    """
    Business Logic Service for Stories.
    Handles retrieving unexpired stories (24-hour expiration) and serializing active stories.
    """

    @staticmethod
    def get_active_stories_grouped():
        """
        Returns active stories (unexpired) grouped by author User object.
        """
        now = timezone.now()
        active_stories = Story.objects.filter(expires_at__gt=now).select_related("author", "author__profile").order_by("-created_at")

        user_stories = {}
        for story in active_stories:
            if story.author not in user_stories:
                user_stories[story.author] = []
            user_stories[story.author].append(story)
        return user_stories

    @staticmethod
    def get_user_active_stories(user):
        """
        Returns active stories for a specific user.
        """
        now = timezone.now()
        return Story.objects.filter(author=user, expires_at__gt=now).order_by("created_at")

    @staticmethod
    def serialize_user_stories(author):
        """
        Returns a list of dict payloads for an author's active stories.
        """
        stories = StoryService.get_user_active_stories(author)
        payload = []
        for s in stories:
            image_url = s.image.url if s.image else ""
            payload.append({
                "id": s.id,
                "image_url": image_url,
                "caption": s.caption,
                "created_at": s.created_at.strftime("%I:%M %p"),
            })
        return payload
