from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .services import InteractionService, NotificationService
from .models import Notification


# =========================================================
# ADD COMMENT CONTROLLER (AJAX)
# =========================================================
@login_required
def add_comment(request, post_id):
    """
    AJAX Controller for creating comments on posts.
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    text = request.POST.get("text", "")
    success, data, status_code = InteractionService.add_comment(post_id, request.user, text)

    if not success:
        return JsonResponse({
            "success": False,
            "message": data["message"]
        }, status=status_code)

    return JsonResponse({
        "success": True,
        "comment": data["comment"],
        "comment_count": data["comment_count"]
    })


# =========================================================
# DELETE COMMENT CONTROLLER (AJAX)
# =========================================================
@login_required
def delete_comment(request, comment_id):
    """
    AJAX Controller for deleting comments.
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    success, data, status_code = InteractionService.delete_comment(comment_id, request.user)

    if not success:
        return JsonResponse({
            "success": False,
            "message": data["message"]
        }, status=status_code)

    return JsonResponse({
        "success": True,
        "comment_count": data["comment_count"]
    })


# =========================================================
# FOLLOW REQUESTS LIST PAGE
# =========================================================
@login_required
def follow_requests(request):
    """
    Renders follow requests dashboard for current user.
    """
    requests_list = InteractionService.get_pending_requests(request.user)
    return render(request, "requests.html", {
        "follow_requests": requests_list
    })


# =========================================================
# ACCEPT FOLLOW REQUEST (AJAX / POST)
# =========================================================
@login_required
def accept_request(request, request_id):
    """
    Accepts a pending follow request.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    success, data, status_code = InteractionService.accept_follow_request(request.user, request_id)

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    if is_ajax:
        if not success:
            return JsonResponse({"success": False, "message": data["message"]}, status=status_code)
        return JsonResponse({"success": True, **data})

    if success:
        messages.success(request, data["message"])
    else:
        messages.error(request, data["message"])
    return redirect("follow_requests")


# =========================================================
# REJECT FOLLOW REQUEST (AJAX / POST)
# =========================================================
@login_required
def reject_request(request, request_id):
    """
    Rejects a pending follow request.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    success, data, status_code = InteractionService.reject_follow_request(request.user, request_id)

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    if is_ajax:
        if not success:
            return JsonResponse({"success": False, "message": data["message"]}, status=status_code)
        return JsonResponse({"success": True, **data})

    if success:
        messages.info(request, data["message"])
    else:
        messages.error(request, data["message"])
    return redirect("follow_requests")


# =========================================================
# NOTIFICATIONS LIST PAGE
# =========================================================
@login_required
def notifications_list(request):
    """
    Renders notifications page for current user.
    """
    filter_type = request.GET.get("filter", "all")
    notifications = NotificationService.get_user_notifications(request.user, filter_type=filter_type)
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return render(request, "notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count,
        "current_filter": filter_type,
    })


# =========================================================
# OPEN NOTIFICATION (CLICK TARGET)
# =========================================================
@login_required
def open_notification(request, notification_id):
    """
    Marks notification as read and redirects user to target content URL.
    """
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save()
    target_url = NotificationService.get_target_url(notif)
    return redirect(target_url)


# =========================================================
# MARK NOTIFICATION READ (AJAX / POST)
# =========================================================
@login_required
def mark_notification_read(request, notification_id):
    """
    AJAX handler to mark a single notification as read.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    success, unread_count = NotificationService.mark_as_read(request.user, notification_id)
    return JsonResponse({
        "success": success,
        "unread_count": unread_count
    })


# =========================================================
# MARK ALL NOTIFICATIONS READ (AJAX / POST)
# =========================================================
@login_required
def mark_all_notifications_read(request):
    """
    AJAX / POST handler to mark all notifications for current user as read.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    success, unread_count = NotificationService.mark_all_as_read(request.user)

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    if is_ajax:
        return JsonResponse({
            "success": True,
            "unread_count": 0,
            "message": "All notifications marked as read."
        })

    messages.success(request, "All notifications marked as read.")
    return redirect("notifications_list")