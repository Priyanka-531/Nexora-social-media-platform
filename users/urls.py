from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.user_login,
        name="login"
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),

    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "profile/<str:username>/",
        views.profile,
        name="user_profile"
    ),

    path(
        "edit-profile/",
        views.edit_profile,
        name="edit_profile"
    ),
     path(
        "follow/<str:username>/",
        views.toggle_follow,
        name="toggle_follow"
    ),

    path(
        "search/",
        views.search_users,
        name="search_users"
    ),

    path(
        "requests/",
        __import__('interactions.views', fromlist=['follow_requests']).follow_requests,
        name="requests"
    ),

    path(
        "notifications/",
        __import__('interactions.views', fromlist=['notifications_list']).notifications_list,
        name="notifications"
    ),

]