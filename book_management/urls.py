# -*- coding: utf-8 -*-

from django.urls import path

from book_management.views import (
    AddNewBookView,
    BookDetailView,
    UdateBookView,
    BookDeleteView,
    BookBorrowRequestView,
    ApproveBorrowRequestView,
    ReturnBorrowBookView,
    MyBorrowedBookList,
    AllPendingApprovalBookListView,
)


urlpatterns = [

    path("add/new/book/", AddNewBookView.as_view(), name="librarian-add-new-book"),

    path("view/book/<int:pk>/detail/", BookDetailView.as_view(), name="librarian-view-particular-book-detail"),

    path("update/book/<int:pk>/detail/", UdateBookView.as_view(), name="librarian-update-book-details"),

    path("delete/book/<int:pk>/", BookDeleteView.as_view(), name="librarian-delete-user"),
    
    path("borrow/book/<int:pk>/", BookBorrowRequestView.as_view(), name="book-borrow-request"),

    path("my/borrowed/book/list/", MyBorrowedBookList.as_view(), name="my-borrowed-book-list"),
    
    path("approve/book/borrow/<int:pk>/", ApproveBorrowRequestView.as_view(), name="librarian-book-borrow-approve-request"),
    path("return/borrow/book/<int:pk>/", ReturnBorrowBookView.as_view(), name="member-return-book-request"),

    path("all/approval/pending/borrowed/request/", AllPendingApprovalBookListView.as_view(), name="all-pending-borrowed-approval-book-list"),
]
