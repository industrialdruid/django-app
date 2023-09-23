from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    login_view,
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    logout_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    ProfileListView,
    ProfileDetailView,
    ProfileUpdateView,
    HelloView,
)


app_name = "myauth"

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    # path("login/", login_view, name="login"),
    path("login/",
         LoginView.as_view(template_name="myauth/login.html",
                           redirect_authenticated_user=True),
         name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),

    path("profiles/", ProfileListView.as_view(), name="profile-list"),
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile_detail"),
    path("profiles/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile_update")
]