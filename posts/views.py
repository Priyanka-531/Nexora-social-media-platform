from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .services import PostService


# =========================================================
# CREATE POST CONTROLLER
# =========================================================
@login_required
def create_post(request):
    """
    Controller for handling post creation.
    """
    if request.method == "POST":
        form = PostService.get_post_form(request.POST, request.FILES)
        post, success = PostService.create_post(request.user, form)
        if success:
            messages.success(request, "Post published successfully!")
            return redirect("home")
        else:
            messages.error(request, "Failed to create post. Please check the form errors below.")
    else:
        form = PostService.get_post_form()

    return render(
        request,
        "create_post.html",
        {
            "form": form
        }
    )


# =========================================================
# LIKE / UNLIKE POST CONTROLLER (AJAX)
# =========================================================
@login_required
def like_post(request, post_id):
    """
    AJAX Controller for toggling likes on posts.
    """
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    import json
    force_like = False
    if request.content_type == "application/json" and request.body:
        try:
            body_data = json.loads(request.body)
            force_like = bool(body_data.get("force_like", False))
        except Exception:
            pass
    if not force_like:
        force_like = request.POST.get("force_like") == "true"

    success, liked, likes_count = PostService.toggle_like(request.user, post_id, force_like=force_like)

    return JsonResponse(
        {
            "success": True,
            "liked": liked,
            "likes_count": likes_count,
        }
    )



# =========================================================
# SAVE / BOOKMARK POST CONTROLLER (AJAX)
# =========================================================
@login_required
def save_post(request, post_id):
    """
    AJAX Controller for toggling bookmark/saved state on posts.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Please log in to save posts."
            },
            status=401
        )

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    success, saved, message = PostService.toggle_save(request.user, post_id)

    return JsonResponse(
        {
            "success": True,
            "saved": saved,
            "message": message,
        }
    )


# =========================================================
# DELETE POST CONTROLLER (Supports both Form and AJAX)
# =========================================================
@login_required
def delete_post(request, post_id):
    """
    Controller for deleting user posts.
    Supports both standard HTML form POST redirects and AJAX JSON responses.
    """
    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    if request.method != "POST":
        if is_ajax:
            return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
        messages.error(request, "Invalid request method.")
        return redirect("home")

    success, message, status_code = PostService.delete_post(request.user, post_id)

    if is_ajax:
        if not success:
            return JsonResponse({"success": False, "message": message}, status=status_code)
        return JsonResponse({"success": True})

    # Standard Form Submit Redirect
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    redirect_url = request.META.get("HTTP_REFERER") or "home"
    return redirect(redirect_url)


# =========================================================
# USER STORIES API CONTROLLER (AJAX)
# =========================================================
def user_stories_api(request, username):
    """
    AJAX endpoint returning JSON payload of active stories for a given username.
    """
    from django.contrib.auth.models import User
    from .services import StoryService

    author = User.objects.filter(username=username).first()
    if not author:
        return JsonResponse({"success": False, "message": "User not found."}, status=404)

    stories = StoryService.serialize_user_stories(author)
    avatar_url = author.profile.profile_picture.url if hasattr(author, "profile") and author.profile.profile_picture else ""

    return JsonResponse({
        "success": True,
        "username": author.username,
        "avatar_url": avatar_url,
        "stories": stories
    })