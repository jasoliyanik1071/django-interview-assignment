# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from book_management.models import (
    BookPublisher,
    BookAuthor,
    Book,
    BookBorrower
)


class BookPublisherAdmin(admin.ModelAdmin):

    list_display = ("name", )
    search_fields = ("name", )
    list_filter = ("name", )
    list_per_page = 15

    class Meta:
        model = BookPublisher


class BookAuthorAdmin(admin.ModelAdmin):

    list_display = ("name", )
    search_fields = ("name", )
    list_filter = ("name", )
    list_per_page = 15

    class Meta:
        model = BookAuthor


class BookAdmin(admin.ModelAdmin):

    list_display = ["title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "created_by", "book_status"]
    # list_display = ["title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "available_copies", "created_by"]
    search_fields = ("title", "author__name", "publisher__name", "publish_year", "book_status")
    list_filter = ("title", "author__name", "publisher__name", "publish_year", "book_status")
    list_per_page = 15

    class Meta:
        model = Book


class BookBorrowerAdmin(admin.ModelAdmin):

    list_display = ["student", "book", "book_issue_date", "book_return_date", "book_issuer", "is_book_issued"]
    search_fields = ("student__username", "book__title", "book_issuer__username", "is_book_issued")
    list_filter = ("student__username", "book__title", "book_issuer__username", "is_book_issued")
    list_per_page = 15

    class Meta:
        model = BookBorrower

admin.site.register(BookPublisher, BookPublisherAdmin)
admin.site.register(BookAuthor, BookAuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookBorrower, BookBorrowerAdmin)