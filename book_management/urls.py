# -*- coding: utf-8 -*-
"""
    - Custom URL's for Book Management
"""

from django.urls import path

from book_management.views import (
    AddNewBookView,
    BookDetailView,
    UpdateBookView,
    DeleteBookView,
    BookBorrowRequestView,
    MyBorrowedBookList,
    ApproveBorrowRequestView,
    ReturnBorrowBookView,
    AllPendingApprovalBookListView,
)

urlpatterns = [
    # API: Add a new book by Librarian User
    path("add/new/book/", AddNewBookView.as_view(), name="librarian-add-new-book"),
    # API: View particular book details
    path(
        "view/book/<int:pk>/detail/",
        BookDetailView.as_view(),
        name="librarian-view-particular-book-detail",
    ),
    # API: Update particular book details as Librarian User
    path(
        "update/book/<int:pk>/detail/",
        UpdateBookView.as_view(),
        name="librarian-update-book-details",
    ),
    # API: Delete particular book as Librarian User
    path(
        "delete/book/<int:pk>/", DeleteBookView.as_view(), name="librarian-delete-user"
    ),
    # API: Request for new book from the library
    path(
        "borrow/book/<int:pk>/",
        BookBorrowRequestView.as_view(),
        name="book-borrow-request",
    ),
    # API: List of all borrowed book by currently logged-in user
    path(
        "my/borrowed/book/list/",
        MyBorrowedBookList.as_view(),
        name="my-borrowed-book-list",
    ),
    # API: Approve the borrow book request by Librarian User
    path(
        "approve/book/borrow/<int:pk>/",
        ApproveBorrowRequestView.as_view(),
        name="librarian-book-borrow-approve-request",
    ),
    # API: Return particular book which is borrowed by user
    path(
        "return/borrow/book/<int:pk>/",
        ReturnBorrowBookView.as_view(),
        name="member-return-book-request",
    ),
    # API: All pending borrow requst as student and manage by Librarian User
    path(
        "all/approval/pending/borrowed/request/",
        AllPendingApprovalBookListView.as_view(),
        name="all-pending-borrowed-approval-book-list",
    ),
]
