from django.urls import path
from . import views


urlpatterns = [

    path(
        "comment/<int:post_id>/",
        views.add_comment,
        name="add_comment"
    ),

    path(
        "delete-comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment"
    ),

    path(
        "requests/",
        views.follow_requests,
        name="follow_requests"
    ),

    path(
        "requests/accept/<int:request_id>/",
        views.accept_request,
        name="accept_follow_request"
    ),

    path(
        "requests/reject/<int:request_id>/",
        views.reject_request,
        name="reject_follow_request"
    ),

    path(
        "notifications/",
        views.notifications_list,
        name="notifications_list"
    ),

    path(
        "notifications/open/<int:notification_id>/",
        views.open_notification,
        name="open_notification"
    ),

    path(
        "notifications/mark-read/<int:notification_id>/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),

    path(
        "notifications/mark-all-read/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read"
    ),

]