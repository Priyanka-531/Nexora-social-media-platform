from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
from .services import UserService
from interactions.services import InteractionService


# =========================================================
# HOME / FEED CONTROLLER
# =========================================================
def home(request):
    """
    Renders main feed with filtered posts (for_you, following, latest, popular, trending), suggested users, and liked post state.
    """
    feed_type = request.GET.get("feed", "for_you")
    context = UserService.get_feed_data(request.user, feed_type=feed_type)
    return render(request, "home.html", context)


# =========================================================
# REGISTER CONTROLLER
# =========================================================
def register(request):
    """
    Handles user registration request and account creation.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        user, success = UserService.register_user(request, form)
        if success:
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# =========================================================
# LOGIN CONTROLLER
# =========================================================
def user_login(request):
    """
    Handles authentication and user session login.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        user, success = UserService.authenticate_and_login(request, form)
        if success:
            messages.success(request, "Logged in successfully!")
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


# =========================================================
# LOGOUT CONTROLLER
# =========================================================
def user_logout(request):
    """
    Handles user logout with confirmation page and logout status template rendering.
    """
    if request.method == "POST" or request.GET.get("confirm") == "true":
        logout(request)
        messages.success(request, "You have been logged out successfully!")
        return render(request, "logout.html", {"logged_out": True})

    if request.user.is_authenticated:
        return render(request, "logout.html", {"confirm_logout": True})

    return render(request, "logout.html", {"logged_out": True})



# =========================================================
# PROFILE CONTROLLER
# =========================================================
@login_required
def profile(request, username=None):
    """
    Displays profile dashboard for target user or current user.
    """
    context = UserService.get_profile_data(request.user, target_username=username)
    return render(request, "profile.html", context)


# =========================================================
# EDIT PROFILE CONTROLLER
# =========================================================
@login_required
def edit_profile(request):
    """
    Handles profile updates and avatar/cover media uploads.
    """
    if request.method == "POST":
        form, profile_obj = UserService.get_edit_profile_form(
            request.user, post_data=request.POST, files_data=request.FILES
        )
        if UserService.save_profile_form(form):
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form, profile_obj = UserService.get_edit_profile_form(request.user)

    return render(request, "edit_profile.html", {"form": form})


from django.db.models import Q


# =========================================================
# FOLLOW / UNFOLLOW CONTROLLER (AJAX & Form)
# =========================================================
def toggle_follow(request, username):
    """
    Handles follow/request/unfollow actions between users via AJAX or form submit.
    """
    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
        or request.content_type == "application/json"
    )

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({"success": False, "message": "Please log in to follow users."}, status=401)
        messages.error(request, "Please log in to follow users.")
        return redirect("login")

    if request.method != "POST" and is_ajax:
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    success, status_str, is_following, is_requested, target_followers, target_following, follower_following, message = InteractionService.toggle_follow(request.user, username)

    if is_ajax:
        if not success:
            return JsonResponse({"success": False, "message": message}, status=400)
        return JsonResponse({
            "success": True,
            "status": status_str,
            "is_following": is_following,
            "is_requested": is_requested,
            "target_followers_count": target_followers,
            "target_following_count": target_following,
            "follower_following_count": follower_following,
            "target_username": username,
            "follower_username": request.user.username,
            "message": message,
        })

    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)

    redirect_url = request.META.get("HTTP_REFERER") or "home"
    return redirect(redirect_url)


# =========================================================
# UNIVERSAL SEARCH CONTROLLER (AJAX & HTML)
# =========================================================
def search_users(request):
    """
    Universal Search Controller for live search dropdown and search results page.
    Supports searching People and Posts with category filtering.
    """
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "all").strip().lower()

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    context = UserService.search_universal(query, request.user, category=category)

    if is_ajax:
        if not query:
            return JsonResponse({"users": [], "posts": [], "query": ""})

        users_payload = []
        for u in context["users"][:5]:
            avatar_url = u.profile.profile_picture.url if hasattr(u, "profile") and u.profile.profile_picture else f"https://ui-avatars.com/api/?name={u.username}&background=6b38d4&color=fff"
            is_following = u.id in context["user_following_ids"]
            is_requested = u.id in context["user_requested_ids"]
            status_val = "following" if is_following else ("requested" if is_requested else "none")

            users_payload.append({
                "id": u.id,
                "username": u.username,
                "full_name": u.get_full_name() or u.username,
                "avatar_url": avatar_url,
                "status": status_val,
                "is_following": is_following,
                "is_requested": is_requested,
                "is_self": request.user.is_authenticated and u.id == request.user.id
            })

        posts_payload = []
        for p in context["posts"][:5]:
            author_avatar = p.author.profile.profile_picture.url if hasattr(p.author, "profile") and p.author.profile.profile_picture else f"https://ui-avatars.com/api/?name={p.author.username}&background=6b38d4&color=fff"
            posts_payload.append({
                "id": p.id,
                "author_username": p.author.username,
                "author_avatar": author_avatar,
                "caption": p.caption[:80] + "..." if len(p.caption) > 80 else p.caption,
                "image_url": p.image.url if p.image else "",
                "created_at": p.created_at.strftime("%b %d"),
                "likes_count": p.likes.count(),
                "comments_count": p.comments.count(),
            })

        return JsonResponse({
            "query": query,
            "users": users_payload,
            "posts": posts_payload,
        })

    return render(request, "search.html", context)