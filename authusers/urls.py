# -*- coding: utf-8 -*-
"""
    - Custom URL's for Account Management
"""

from django.urls import path

from authusers.serializers import CustomJWTSerializer
from authusers.views import (
    ActivateRegisteredUser,
    JSONWebTokenAPIOverride,
    LibrarianRegisterView,
    LogoutView,
    MemberRegisterByLibrarianView,
    MemberRegisterView,
    MemberUserDeleteView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
    index,
)

urlpatterns = [
    # API: Used for Librarian Registration
    path(
        "register/librarian/",
        LibrarianRegisterView.as_view(),
        name="register-librarian-user",
    ),
    # API: Used for Member Registration
    path("register/member/", MemberRegisterView.as_view(), name="register-member-user"),
    # API: Used to register new Member but create Member with the help of Librarian user or
    # Librarian user create member user
    path(
        "librarian/create/member/",
        MemberRegisterByLibrarianView.as_view(),
        name="librarian-create-member",
    ),
    # API: Account verification Link generator
    path(
        "activate/<slug:uidb64>/<slug:token>/",
        ActivateRegisteredUser.as_view(),
        name="useractivation",
    ),
    # API: User Login
    path(
        "user/login/",
        JSONWebTokenAPIOverride.as_view(serializer_class=CustomJWTSerializer),
        name="user-login",
    ),
    # API: Update user details as Librarian user
    path("update/user/<int:pk>/", UserUpdateView.as_view(), name="update-user-details"),
    # API: Update user detail
    path("update/user/", UserUpdateView.as_view(), name="update-user-details"),
    # API: Delete user as Librarian user
    path("delete/user/<int:pk>/", UserDeleteView.as_view(), name="delete-user"),
    # API: Delete user
    path(
        "delete/member/user/", MemberUserDeleteView.as_view(), name="member-delete-user"
    ),
    # API: Logout user
    path("user/logout/", LogoutView.as_view()),
    # API: All Users list with its related details
    path("users/", UserListView.as_view()),
    # API: Particular user details
    path("users/<int:pk>/", UserDetailView.as_view()),
]
