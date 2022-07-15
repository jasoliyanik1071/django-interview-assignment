# -*- coding: utf-8 -*-

from django.urls import path

from book_management.views import (
    AddNewBookView,
    BookDetailView,
    UdateBookView,
    BookDeleteView,
    BookBorrowRequestView,
    ApproveBorrowRequestView,
    ReturnBorrowBookView
)


urlpatterns = [

    path("add/new/book/", AddNewBookView.as_view(), name="librarian-add-new-book"),

    path("view/book/<int:pk>/detail/", BookDetailView.as_view(), name="librarian-view-particular-book-detail"),

    path("update/book/<int:pk>/detail/", UdateBookView.as_view(), name="librarian-update-book-details"),

    path("delete/book/<int:pk>/", BookDeleteView.as_view(), name="librarian-delete-user"),
    
    path("borrow/book/<int:pk>/", BookBorrowRequestView.as_view(), name="book-borrow-request"),
    
    path("approve/book/borrow/<int:pk>/", ApproveBorrowRequestView.as_view(), name="librarian-book-borrow-approve-request"),
    path("return/borrow/book/<int:pk>/", ReturnBorrowBookView.as_view(), name="member-return-book-request"),

    # path("register/member/", MemberRegisterView.as_view(), name="register-member-user"),

    # path("librarian/create/member/", MemberRegisterByLibrarianView.as_view(), name="librarian-create-member"),

    # # path("user/register/", RegisterView.as_view(), name="register-or-create-user"),

    # path('activate/<slug:uidb64>/<slug:token>/', ActivateRegisteredUser.as_view(), name="useractivation"),

    # path("user/login/", JSONWebTokenAPIOverride.as_view(serializer_class=CustomJWTSerializer), name="user-login"),


    # path("user/logout/", LogoutView.as_view()),
    # path("users/", UserListView.as_view()),
    # path("users/<int:pk>/", UserDetailView.as_view()),
]
