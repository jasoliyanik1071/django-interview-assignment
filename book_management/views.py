# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import datetime

from rest_framework import generics, status, mixins, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication
)
from rest_framework.decorators import (
    authentication_classes,
    permission_classes
)
from rest_framework.generics import GenericAPIView

from django.views import View
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login as django_login, logout

from book_management.serializers import (
    BookPublisherSerializer,
    BookAuthorSerializer,
    BookSerializer,
    UpdateBookSerializer,
    BookBorrowerSerializer,
)
from book_management.models import (
    BookPublisher,
    BookAuthor,
    Book,
    BookBorrower
)
from authusers.util import get_current_site, get_formatted_response, JSONWebTokenAuthentication

from authusers.serializers import UserSerializer, UserProfileSerializer, UserDetailSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

log = logging.getLogger(__name__)



class AddNewBookView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    serializer_class = BookSerializer

    def post(self, request, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, you are not authorized user to Add Book!!!"
            return Response(get_formatted_response(200, message, {}))

        new_book_request_payload = request.data.dict()

        book_publisher_obj = book_author_obj = False

        if "author" in new_book_request_payload and new_book_request_payload.get("author"):
            try:
                book_author_obj = get_object_or_404(BookAuthor, id=new_book_request_payload.pop("author"))
            except Exception as e:
                log.info("Requested Book Author is not exist in system!!!")

        if "publisher" in new_book_request_payload and new_book_request_payload.get("publisher"):
            try:
                book_publisher_obj = get_object_or_404(BookPublisher, id=new_book_request_payload.pop("publisher"))
            except Exception as e:
                log.info("Requested Book Author is not exist in system!!!")

        serializer = self.serializer_class(data=new_book_request_payload)
        if serializer.is_valid():
            new_book_obj = serializer.save()
            new_book_obj.created_by = request.user

            if book_publisher_obj:
                new_book_obj.publisher = book_publisher_obj
            if book_author_obj:
                new_book_obj.author = book_author_obj
            new_book_obj.save()

            response_data = dict(serializer.data)

            if response_data["book_status"] == "book_available":
                response_data["book_status"] = "Book AVAILABLE"
            elif response_data["book_status"] == "book_borrow":
                response_data["book_status"] = "Book BORROWED"

            message = "New Book Added Successfully!!!"
            return Response(get_formatted_response(200, message, response_data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def get_object(self):
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def get(self, request, pk, *args, **kwargs):
        book_obj = self.get_object()

        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        serializer = self.serializer_class(book_obj)

        if serializer and self.kwargs["pk"]:
            message = "Fetched Book Details successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class UdateBookView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = Book.objects.all()
    serializer_class = UpdateBookSerializer
    lookup_field = "pk"

    def get_object(self):
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, You don't have rights to update the book details!!!"
            return Response(get_formatted_response(200, message, {}))


        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            updated_book_obj = serializer.save()
            message = "Book updated successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class BookBorrowRequestView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = BookBorrower.objects.all()
    serializer_class = BookBorrowerSerializer
    lookup_field = "pk"

    def get_object(self):
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        book_obj = self.get_object()

        book_borrow_exist = BookBorrower.objects.filter(book=book_obj)
        if book_borrow_exist:
            borrow_book_exist_obj = book_borrow_exist.first()

            if book_obj.book_status != "book_available" and borrow_book_exist_obj.student == request.user:
                message = "You already borrowed this book from the library, Please choose another book!!!"
                return Response(get_formatted_response(200, message))
            else:
                message = "This book is not available in library (This book is already given to another student), Please choose another book or wait for this books avalability!!!"
                return Response(get_formatted_response(200, message))

            if borrow_book_exist_obj.is_book_issued:
                if borrow_book_exist_obj.student == request.user:
                    message = "You have already assigned this book from library, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "This book is already given to another students, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
            else:
                if borrow_book_exist_obj.student == request.user:
                    message = "You already requested this book from library, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "This book is already requested by other student, Please try with other book!!!"
                    return Response(get_formatted_response(200, message))


        new_book_issue_payload = {
            "student": request.user,
            "book": book_obj,
            "book_application_date": datetime.datetime.today().date()
        }

        try:
            book_borrow_request_obj = BookBorrower(**new_book_issue_payload)
            book_borrow_request_obj.save()
            message = "New book request successfully submitted, Librarian will approve your request shortly"
            return Response(get_formatted_response(200, message, BookBorrowerSerializer(book_borrow_request_obj).data))
        except Exception as e:
            message = "Something went wrong while submitting new book request from library!!!"
            return Response(get_formatted_response(400, message))

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class ApproveBorrowRequestView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = BookBorrower.objects.all()
    lookup_field = "pk"

    def get_object(self):
        obj = get_object_or_404(BookBorrower, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, you are not authorized user to Approve Book Borrow Request!!!"
            return Response(get_formatted_response(200, message, {}))


        try:
            book_borrow_obj = self.get_object()
            book_borrow_obj.book_issuer = request.user
            book_borrow_obj.is_book_issued = True
            book_borrow_obj.book_issue_date = datetime.datetime.now().date()
            book_borrow_obj.book.book_status = "book_borrow"
            book_borrow_obj.student.profile.total_books_due += 1
            book_borrow_obj.student.profile.save()
            book_borrow_obj.student.save()
            book_borrow_obj.book.save()
            book_borrow_obj.save()
            message = "Book request Approved successfully, book has been isuued, You can collect book from library!!!"
            return Response(get_formatted_response(200, message))
        except Exception as e:
            message = "Something went wrong while submitting new book request from library!!!"
            return Response(get_formatted_response(400, message))


        issue_book_payload = {
            "book_issue_date": datetime.datetime.today().date(),
        }

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class ReturnBorrowBookView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def get_object(self):
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            book_obj = self.get_object()
        except Exception as e:
            message = "Requested book is not exist in system, Please try after sometime!!!"
            return Response(get_formatted_response(200, message, {}))

        book_borrow_exist = BookBorrower.objects.filter(book=book_obj)

        if not book_borrow_exist.exists():
            message = "This book is not borrowed, So you can't return this book!!!"
            return Response(get_formatted_response(200, message, {}))
        else:
            borrow_book_exist_obj = book_borrow_exist.first()

            if borrow_book_exist_obj.student != request.user:
                message = "This book is borrowed by someone else, So you are not authorized user to return this book!!!"
                return Response(get_formatted_response(200, message))

            if borrow_book_exist_obj.is_book_issued:
                if borrow_book_exist_obj.student == request.user:
                    borrow_book_exist_obj.is_book_issued = False
                    borrow_book_exist_obj.book_return_date = datetime.datetime.now().date()
                    borrow_book_exist_obj.book.book_status = "book_available"
                    borrow_book_exist_obj.student.profile.total_books_due -= 1
                    borrow_book_exist_obj.student.profile.save()
                    borrow_book_exist_obj.student.save()
                    borrow_book_exist_obj.book.save()
                    borrow_book_exist_obj.save()

                    borrow_book_exist_obj.delete()
                    message = "Book return successfully to Library, Thanks you!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "This book is not borrowed by you, So you don't have authorized user to return this book!!!"
                    return Response(get_formatted_response(200, message))
            else:
                if borrow_book_exist_obj.student == request.user:
                    message = "You only requested this book from library but This book is not issued yet, So you are not eligible to return this book!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "Someone requested this book from library but you are not authorized user to return this book!!!"
                    return Response(get_formatted_response(200, message))

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))

class BookDeleteView(generics.RetrieveUpdateDestroyAPIView, APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, you are not authorized user to Delete Book!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user and self.kwargs.get("pk"):
            try:
                self.get_object().delete()
                message = "Book Deleted successfully!!!"
                return Response(get_formatted_response(200, message, {}))
                # del_book_obj = self.get_object()
                # serializer = self.serializer_class(del_book_obj)
                # del_book_obj.delete()
                # message = "Book Deleted successfully!!!"
                # return Response(get_formatted_response(200, message, serializer.data))
            except Exception as e:
                message = "Something went wrgon while deleting the user!!!"
                return Response(get_formatted_response(400, message, {}))
        else:
            message = "Something went wrong, Please check the request data and then try again!!!"
            return Response(get_formatted_response(400, message, {}))

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class MyBorrowedBookList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.filter(id__in=BookBorrower.objects.filter(student=self.request.user).values_list("book", flat=True))

    def get(self, request, *args, **kwargs):
        if self.request and not self.request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message))

        if not self.request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message))

        if not hasattr(self.request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message))

        try:
            resp = self.list(request, *args, **kwargs)
            message = "Fetched All Users Details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = "Something went wrong while fetching Users Details!!!"
            return Response(get_formatted_response(400, message, {}))


class AllPendingApprovalBookListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = BookBorrower.objects.all()
    serializer_class = BookBorrowerSerializer

    def get(self, request, *args, **kwargs):
        if self.request and not self.request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message))

        if not self.request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message))

        if not hasattr(self.request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message))

        if self.request.user.profile.is_member and not self.request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to see pending approval requests!!!"
            return Response(get_formatted_response(200, message))

        try:
            resp = self.list(request, *args, **kwargs)
            message = "Fetched All Users Details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = "Something went wrong while fetching Users Details!!!"
            return Response(get_formatted_response(400, message, {}))