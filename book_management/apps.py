# -*- coding: utf-8 -*-
"""
    - Apps file to manage table level things in DB level
"""
from django.apps import AppConfig


class BookManagementConfig(AppConfig):
    """
    - Used to manage app related configuration
    - i.e: If need to create signals then will manage ready method from here
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "book_management"
