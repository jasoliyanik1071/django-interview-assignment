# -*- coding: utf-8 -*-

from django.urls import path

from authusers.serializers import CustomJWTSerializer
from authusers.views import (
    index,
    LibrarianRegisterView,
    MemberRegisterView,
    MemberRegisterByLibrarianView,
    UserUdateView,
    UserDeleteView,
    MemberUserDeleteView,
    LogoutView,
    UserListView,
    UserDetailView,
    JSONWebTokenAPIOverride,
    ActivateRegisteredUser
)


urlpatterns = [

    path("register/librarian/", LibrarianRegisterView.as_view(), name="register-librarian-user"),
    path("register/member/", MemberRegisterView.as_view(), name="register-member-user"),

    path("librarian/create/member/", MemberRegisterByLibrarianView.as_view(), name="librarian-create-member"),

    # path("user/register/", RegisterView.as_view(), name="register-or-create-user"),

    path('activate/<slug:uidb64>/<slug:token>/', ActivateRegisteredUser.as_view(), name="useractivation"),

    path("user/login/", JSONWebTokenAPIOverride.as_view(serializer_class=CustomJWTSerializer), name="user-login"),

    path("update/user/<int:pk>/", UserUdateView.as_view(), name="update-user-details"),
    path("update/user/", UserUdateView.as_view(), name="update-user-details"),
    path("delete/user/<int:pk>/", UserDeleteView.as_view(), name="delete-user"),

    path("delete/member/user/", MemberUserDeleteView.as_view(), name="member-delete-user"),

    path("user/logout/", LogoutView.as_view()),
    path("users/", UserListView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
]
