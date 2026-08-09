from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404
from interactions.models import Follow, FollowRequest
from posts.models import Post
from .models import Profile
from .forms import RegisterForm, EditProfileForm


class UserService:
    """
    Business Logic Service for User Accounts and Profiles.
    Handles user state, profile management, and feeds.
    """

    @staticmethod
    def get_feed_data(user, feed_type="for_you"):
        """
        Retrieves filtered feed posts based on feed_type (for_you, following, latest, popular, trending),
        suggested users to follow, active stories, and IDs of posts liked or saved by the user.
        Uses Prefetch and select_related to eliminate N+1 queries.
        """
        from django.db.models import Count, Q, Case, When, Value, IntegerField, Prefetch
        from django.utils import timezone
        from posts.models import Story
        from interactions.models import Comment

        feed_type = feed_type.lower().strip() if feed_type else "for_you"
        if feed_type not in ["for_you", "following", "latest", "popular", "trending"]:
            feed_type = "for_you"

        following_ids = []
        requested_ids = []

        if user.is_authenticated:
            from interactions.services import InteractionService
            InteractionService.seed_welcome_interactions(user)
            following_ids = list(Follow.objects.filter(follower=user).values_list("following_id", flat=True))
            requested_ids = list(FollowRequest.objects.filter(sender=user, status="pending").values_list("receiver_id", flat=True))

        comments_prefetch = Prefetch(
            "comments",
            queryset=Comment.objects.select_related("user", "user__profile").order_by("created_at")
        )

        base_qs = Post.objects.select_related("author", "author__profile").prefetch_related(comments_prefetch)

        # Build feed QuerySet according to feed_type
        if feed_type == "following":
            if user.is_authenticated:
                posts = base_qs.filter(
                    Q(author_id__in=following_ids) | Q(author=user)
                ).order_by("-created_at")
            else:
                posts = Post.objects.none()

        elif feed_type == "latest":
            posts = base_qs.order_by("-created_at")

        elif feed_type == "popular":
            posts = base_qs.annotate(
                engagement=Count("likes", distinct=True) + Count("comments", distinct=True)
            ).order_by("-engagement", "-created_at")

        elif feed_type == "trending":
            posts = base_qs.annotate(
                engagement=Count("likes", distinct=True) + Count("comments", distinct=True)
            ).order_by("-created_at", "-engagement")

        else:
            # For You (Default)
            if user.is_authenticated and following_ids:
                posts = base_qs.annotate(
                    is_followed=Case(
                        When(Q(author_id__in=following_ids) | Q(author=user), then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ).order_by("-is_followed", "-created_at")
            else:
                posts = base_qs.order_by("-created_at")

        suggested_users = []
        liked_post_ids = []
        saved_post_ids = []

        now = timezone.now()
        active_story_user_ids = set(
            Story.objects.filter(expires_at__gt=now).values_list("author_id", flat=True)
        )

        if user.is_authenticated:
            exclude_ids = set(following_ids + requested_ids + [user.id])
            suggested_users = User.objects.exclude(id__in=exclude_ids).select_related("profile")[:8]
            liked_post_ids = list(Post.objects.filter(likes=user).values_list("id", flat=True))
            saved_post_ids = list(Post.objects.filter(saved_by=user).values_list("id", flat=True))
        else:
            suggested_users = User.objects.all().select_related("profile")[:8]

        return {
            "posts": posts,
            "current_feed": feed_type,
            "suggested_users": suggested_users,
            "liked_post_ids": liked_post_ids,
            "saved_post_ids": saved_post_ids,
            "active_story_user_ids": active_story_user_ids,
        }

    @staticmethod
    def register_user(request, form):
        """
        Registers a new user and automatically logs them in upon successful form validation.
        Also seeds initial follow requests & notifications for instant interaction.
        """
        from interactions.services import InteractionService
        if form.is_valid():
            user = form.save()
            login(request, user)
            InteractionService.seed_welcome_interactions(user)
            return user, True
        return None, False

    @staticmethod
    def authenticate_and_login(request, form):
        """
        Authenticates user credentials and initiates session login upon successful validation.
        Also seeds initial follow requests & notifications for instant interaction.
        """
        from interactions.services import InteractionService
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                InteractionService.seed_welcome_interactions(user)
                return user, True
        return None, False

    @staticmethod
    def get_profile_data(current_user, target_username=None):
        """
        Fetches profile details, posts, liked posts, saved posts, follow status, requested status, and follower/following counts.
        Uses Prefetch to optimize comments and user relationships.
        """
        from django.db.models import Prefetch
        from interactions.models import Comment

        if target_username:
            profile_user = get_object_or_404(User, username=target_username)
        else:
            profile_user = current_user

        profile, _ = Profile.objects.get_or_create(user=profile_user)

        comments_prefetch = Prefetch(
            "comments",
            queryset=Comment.objects.select_related("user", "user__profile").order_by("created_at")
        )

        user_posts = Post.objects.filter(author=profile_user).select_related("author", "author__profile").prefetch_related(comments_prefetch).order_by("-created_at")
        liked_posts = profile_user.liked_posts.select_related("author", "author__profile").prefetch_related(comments_prefetch).order_by("-created_at")
        saved_posts = profile_user.saved_posts.select_related("author", "author__profile").prefetch_related(comments_prefetch).order_by("-created_at")

        is_following = False
        is_requested = False
        if current_user.is_authenticated and current_user != profile_user:
            is_following = Follow.objects.filter(
                follower=current_user,
                following=profile_user
            ).exists()
            if not is_following:
                is_requested = FollowRequest.objects.filter(
                    sender=current_user,
                    receiver=profile_user,
                    status="pending"
                ).exists()

        followers_qs = Follow.objects.filter(following=profile_user).select_related("follower__profile")
        following_qs = Follow.objects.filter(follower=profile_user).select_related("following__profile")

        followers_list = [f.follower for f in followers_qs]
        following_list = [f.following for f in following_qs]

        user_following_ids = set()
        user_requested_ids = set()
        if current_user.is_authenticated:
            user_following_ids = set(Follow.objects.filter(follower=current_user).values_list("following_id", flat=True))
            user_requested_ids = set(FollowRequest.objects.filter(sender=current_user, status="pending").values_list("receiver_id", flat=True))

        from django.utils import timezone
        from posts.models import Story

        has_active_story = Story.objects.filter(author=profile_user, expires_at__gt=timezone.now()).exists()

        return {
            "profile": profile,
            "profile_user": profile_user,
            "user_posts": user_posts,
            "liked_posts": liked_posts,
            "saved_posts": saved_posts,
            "is_following": is_following,
            "is_requested": is_requested,
            "followers_count": len(followers_list),
            "following_count": len(following_list),
            "followers_list": followers_list,
            "following_list": following_list,
            "user_following_ids": user_following_ids,
            "user_requested_ids": user_requested_ids,
            "has_active_story": has_active_story,
        }

    @staticmethod
    def get_edit_profile_form(user, post_data=None, files_data=None):
        """
        Retrieves or processes the edit profile form for a given user.
        """
        profile, _ = Profile.objects.get_or_create(user=user)
        if post_data is not None:
            form = EditProfileForm(post_data, files_data, instance=profile)
        else:
            form = EditProfileForm(instance=profile)
        return form, profile

    @staticmethod
    def save_profile_form(form):
        """
        Saves profile updates if form is valid.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def search_universal(query, current_user, category="all"):
        """
        Performs case-insensitive partial search across users (username, name, bio, profession)
        and posts (caption, author username/name). Returns structured context with follow states.
        Uses Count annotations to eliminate N+1 queries.
        """
        query = query.strip() if query else ""
        if not query:
            return {
                "query": "",
                "category": category,
                "users": [],
                "posts": [],
                "users_count": 0,
                "posts_count": 0,
                "user_following_ids": set(),
                "user_requested_ids": set(),
                "liked_post_ids": [],
                "saved_post_ids": [],
            }

        from django.db.models import Q, Count, Prefetch
        from interactions.models import Comment

        comments_prefetch = Prefetch(
            "comments",
            queryset=Comment.objects.select_related("user", "user__profile").order_by("created_at")
        )

        # People Query
        users_qs = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__bio__icontains=query) |
            Q(profile__profession__icontains=query)
        ).distinct().select_related("profile")

        # Posts Query
        posts_qs = Post.objects.filter(
            Q(caption__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).distinct().select_related("author", "author__profile").prefetch_related(comments_prefetch).annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True)
        ).order_by("-created_at")

        user_following_ids = set()
        user_requested_ids = set()
        liked_post_ids = []
        saved_post_ids = []

        if current_user.is_authenticated:
            user_following_ids = set(Follow.objects.filter(follower=current_user).values_list("following_id", flat=True))
            user_requested_ids = set(FollowRequest.objects.filter(sender=current_user, status="pending").values_list("receiver_id", flat=True))
            liked_post_ids = list(posts_qs.filter(likes=current_user).values_list("id", flat=True))
            saved_post_ids = list(posts_qs.filter(saved_by=current_user).values_list("id", flat=True))

        users_list = list(users_qs)
        posts_list = list(posts_qs)

        return {
            "query": query,
            "category": category,
            "users": users_list,
            "posts": posts_list,
            "users_count": len(users_list),
            "posts_count": len(posts_list),
            "user_following_ids": user_following_ids,
            "user_requested_ids": user_requested_ids,
            "liked_post_ids": liked_post_ids,
            "saved_post_ids": saved_post_ids,
        }


