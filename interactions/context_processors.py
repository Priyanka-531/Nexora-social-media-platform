from .models import FollowRequest, Notification


def pending_requests(request):
    """
    Context processor to make pending follow requests count and unread notifications count globally available in templates.
    """
    if request.user.is_authenticated:
        req_count = FollowRequest.objects.filter(
            receiver=request.user,
            status="pending"
        ).count()
        unread_notif_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related("sender__profile", "post", "post__author")[:6]

        return {
            "pending_follow_requests_count": req_count,
            "unread_notifications_count": unread_notif_count,
            "navbar_notifications": recent_notifications,
        }
    return {
        "pending_follow_requests_count": 0,
        "unread_notifications_count": 0,
        "navbar_notifications": [],
    }

