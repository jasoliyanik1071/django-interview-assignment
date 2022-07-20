# -*- coding: utf-8 -*-
"""
    - Used to manage admin view for auth-users custom app
"""
from __future__ import unicode_literals

from django.contrib import admin

from authusers.models import Branch, UserProfile


class BranchAdmin(admin.ModelAdmin):
    """
    - Used to Manage Branch view in Admin side
    """

    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    list_per_page = 15

    class Meta:
        """
        - Defined meta class
        """

        model = Branch


class UserProfileAdmin(admin.ModelAdmin):
    """
    - Used to Manage User-Profile view in Admin side
    """

    list_display = (
        "user",
        "roll_no",
        "first_name",
        "last_name",
        "mobile",
        "branch",
        "is_librarian",
        "is_member",
        "total_books_due",
        "created_by",
    )
    search_fields = (
        "roll_no",
        "user__username",
        "first_name",
        "last_name",
        "mobile",
        "branch__name",
        "created_by",
    )
    list_filter = (
        "roll_no",
        "user__username",
        "first_name",
        "last_name",
        "mobile",
        "branch__name",
        "is_librarian",
        "is_member",
        "total_books_due",
        "created_by__username",
    )
    list_per_page = 15

    class Meta:
        """
        - Defined meta class
        """

        model = UserProfile


# Register all the custom created tables in admin side
admin.site.register(Branch, BranchAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
