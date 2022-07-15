# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from authusers.models import UserProfile, Branch


class BranchAdmin(admin.ModelAdmin):

    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    list_per_page = 15

    class Meta:
        model = Branch


class UserProfileAdmin(admin.ModelAdmin):

    list_display = ("user", "roll_no", "first_name", "last_name", "mobile", "branch", "is_librarian", "is_member", "total_books_due", "created_by")
    search_fields = ("roll_no", "user__username", "first_name", "last_name", "mobile", "branch__name", "created_by")
    list_filter = ("roll_no", "user__username", "first_name", "last_name", "mobile", "branch__name", "is_librarian", "is_member", "total_books_due", "created_by__username")
    list_per_page = 15

    class Meta:
        model = UserProfile


admin.site.register(Branch, BranchAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
