# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from rest_framework import exceptions, serializers


from authusers.serializers import UserSerializer, UserDetailSerializer, UserProfileSerializer

from book_management.models import (
    BookPublisher,
    BookAuthor,
    Book,
    BookBorrower
)


class BookPublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookPublisher
        fields = ("id", "name",)


class BookAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookAuthor
        fields = ("id", "name",)


class BookSerializer(serializers.ModelSerializer):

    publisher = BookPublisherSerializer(required=False)
    author = BookAuthorSerializer(required=False)
    created_by = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Book
        depth = 3
        fields = ["id", "title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "created_by", "book_status"]
        # fields = ["id", "title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "available_copies", "created_by"]


class UpdateBookSerializer(serializers.ModelSerializer):

    publisher = BookPublisherSerializer(required=False)
    author = BookAuthorSerializer(required=False)
    created_by = UserSerializer(required=False, read_only=True)

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.subtitle = validated_data.get("subtitle", instance.subtitle)
        instance.summary = validated_data.get("summary", instance.summary)
        instance.isbn = validated_data.get("isbn", instance.isbn)
        instance.author = validated_data.get("author", instance.author)
        instance.publisher = validated_data.get("publisher", instance.publisher)
        instance.publish_year = validated_data.get("publish_year", instance.publish_year)
        # instance.available_copies = validated_data.get("available_copies", instance.available_copies)
        instance.save()
        return instance

    class Meta:
        model = Book
        depth = 3
        fields = ["id", "title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "created_by", "book_status"]
        # fields = ["id", "title", "subtitle", "summary", "isbn", "author", "publisher", "publish_year", "available_copies", "created_by"]


class BookBorrowerSerializer(serializers.ModelSerializer):

    student = UserDetailSerializer(required=False)
    book = BookSerializer(required=False)
    book_issuer = UserDetailSerializer(required=False)

    class Meta:
        fields = ["id", "student", "book", "book_application_date", "book_issue_date", "book_return_date", "book_issuer"]
        model = BookBorrower
        depth = 3
