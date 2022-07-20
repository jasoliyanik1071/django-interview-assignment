# -*- coding: utf-8 -*-
"""
    - Business logic for Book Management API's
    - All the APIs related to Book Manage is in this file

    - i.e:
        01). API: Add new Book by Librarian User
            - AddNewBookView

        02). API: View particular Book Details by Librarian User
            - BookDetailView

        03). API: Update Book Details by Librarian User
            - UpdateBookView

        04). API: Delete Particular Book by Librarian User
            - DeleteBookView

        05). API: Borrow new Book as Student/Member User
            - BookBorrowRequestView

        06). API: My Borrowed all book list by Member/Student
            - MyBorrowedBookList

        07). API: Approve borrow book
            - ApproveBorrowRequestView

        08). API: Return book by Student/Member
            - ReturnBorrowBookView
            
        09). API: All pending borrow request list by Librarian User
            - AllPendingApprovalBookListView
"""
from __future__ import unicode_literals

import datetime
import logging

# Default Django import
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

# 3rd party DRF imports
from rest_framework import generics, mixins, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Custom App (AuthUsers) imports
from authusers.util import (
    JSONWebTokenAuthentication,
    get_formatted_response,
)

# Custom App (Book-Management) imports
from book_management.models import Book, BookAuthor, BookBorrower, BookPublisher
from book_management.serializers import (
    BookBorrowerSerializer,
    BookSerializer,
    UpdateBookSerializer,
)

log = logging.getLogger(__name__)


class AddNewBookView(generics.GenericAPIView):

    """
    POST: Add New Book API

    :param:
        - title:
            - Store the Title of the Book
        - subtitle:
            - Store the Subtitle of the Book
        - summary:
            - Store the Short summary of the Book
        - isbn:
            - Store the ISBN of the Book
        - author:
            - Store the Author of the Book
        - publisher:
            - Store the Book Publisher
        - publish_year:
            - Store the Publish Year of the Book
        - book_status:
            - Store the Book status (Borrowed or Available)

    SET:
        ::created_by:
            - Store the Who created this record
    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    serializer_class = BookSerializer

    def post(self, request, *args, **kwargs):
        """
        - Create a new book object
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if profile is exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # As of now only librarian has right to create new book
        # Check if currently logged-in user member or librarian
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to Add Book!!!"
            return Response(get_formatted_response(200, message, {}))

        new_book_request_payload = request.data.dict()

        book_publisher_obj = book_author_obj = False

        # Get the Auther instance object if 'author' is exist in request payload
        if "author" in new_book_request_payload and new_book_request_payload.get(
            "author"
        ):
            try:
                book_author_obj = get_object_or_404(
                    BookAuthor, id=new_book_request_payload.pop("author")
                )
            except Exception as e:
                log.info("Requested Book Author is not exist in system!!!")

        # Get the Publisher instance object if 'publisher' is exist in request payload
        if "publisher" in new_book_request_payload and new_book_request_payload.get(
            "publisher"
        ):
            try:
                book_publisher_obj = get_object_or_404(
                    BookPublisher, id=new_book_request_payload.pop("publisher")
                )
            except Exception as e:
                log.info("Requested Book Author is not exist in system!!!")

        # Serialize the requested payload
        serializer = self.serializer_class(data=new_book_request_payload)

        # Validate the book-serializer
        if serializer.is_valid():
            # If validate properly then save the book instance
            new_book_obj = serializer.save()

            # Save created-by from the currently logged-in user
            new_book_obj.created_by = request.user

            # Save the publisher instance
            if book_publisher_obj:
                new_book_obj.publisher = book_publisher_obj
            # Save the author instance
            if book_author_obj:
                new_book_obj.author = book_author_obj
            new_book_obj.save()

            response_data = dict(serializer.data)

            # Set the book status
            if response_data["book_status"] == "book_available":
                response_data["book_status"] = "Book AVAILABLE"
            elif response_data["book_status"] == "book_borrow":
                response_data["book_status"] = "Book BORROWED"

            message = "New Book Added Successfully!!!"
            return Response(get_formatted_response(200, message, response_data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(generics.RetrieveAPIView):

    """
    GET: Fetch particular Book Details API

    :param:
        - id:
            - ID of that account which you want to delete as Librarian user

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Get the book instance to view particular book ID/PK
        """
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def get(self, request, pk, *args, **kwargs):
        """
        GET the particular book details
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check currently logged-in user has profile exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Get the book object
        try:
            # Get the book
            book_obj = self.get_object()
        except Exception as e:
            message = (
                "Requested book is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Serialize the book
        serializer = self.serializer_class(book_obj)

        # Fetch the serialize the book-serialize data and return
        if serializer and self.kwargs["pk"]:
            message = "Fetched Book Details successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class UpdateBookView(generics.RetrieveAPIView, mixins.UpdateModelMixin):

    """
    PUT: Update particular book details API

    :param:
        - id:
            - ID of that book which you want to update the details
        - title:
            - Store the Title of the Book
        - subtitle:
            - Store the Subtitle of the Book
        - summary:
            - Store the Short summary of the Book
        - isbn:
            - Store the ISBN of the Book
        - author:
            - Store the Author of the Book
        - publisher:
            - Store the Book Publisher
        - publish_year:
            - Store the Publish Year of the Book
        - book_status:
            - Store the Book status (Borrowed or Available)

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = Book.objects.all()
    serializer_class = UpdateBookSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Get the book instance to view particular book ID/PK
        """
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def put(self, request, *args, **kwargs):
        """
        PUT: Update particular book details API

        - Default method of CBV
        - Will override this method and update the payload related data to requested book
        """
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        - This method used to manipulate the book details
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check currently logged-in user has profile or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # As of now only Librarian allows to update/manipulate the book details so check the role/permission
        # Check if currently logged-in user is member or librarian?
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, You don't have rights to update the book details!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            # Fetch the book object
            instance = self.get_object()
        except Exception as e:
            message = (
                "Requested book is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Serialize the book instance and update the requested/updated book details
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        # Validate the book details
        if serializer.is_valid():
            # If valid success then update the book instance/object
            updated_book_obj = serializer.save()
            message = "Book updated successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class BookBorrowRequestView(generics.GenericAPIView):

    """
    POST: Add New Book API

    :param:
        - student:
            - Get from request user
            - Currently logged-in user
        - book:
            - Which book wants to borrow by currently logged-in user

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = BookBorrower.objects.all()
    serializer_class = BookBorrowerSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Get the book instance to view particular book ID/PK
        """
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        """
        POST: Add New Book API
        - Request for new book borrow by student
        """
        # Check if user is exist in request or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check currently logged-in user has profile or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Fetch the book instance/object
        try:
            # Fetch the book object
            book_obj = self.get_object()
        except Exception as e:
            message = (
                "Requested book is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Filter the book in borrow table to check this book is already given to other student/member or not?
        book_borrow_exist = BookBorrower.objects.filter(book=book_obj)
        if book_borrow_exist:
            borrow_book_exist_obj = book_borrow_exist.first()

            # Check if book status is borrowed then raise the error message
            if (
                book_obj.book_status != "book_available"
                and borrow_book_exist_obj.student == request.user
            ):
                message = "You already borrowed this book from the library, Please choose another book!!!"
                return Response(get_formatted_response(200, message))
            else:
                message = "This book is not available in library (This book is already given to another student), Please choose another book or wait for this books avalability!!!"
                return Response(get_formatted_response(200, message))

            # Check if book is already issued to someone else
            if borrow_book_exist_obj.is_book_issued:
                # Check if already issued to currently logged-in user or other student/member
                if borrow_book_exist_obj.student == request.user:
                    message = "You have already assigned this book from library, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "This book is already given to another students, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
            else:
                # Check if book is not issued and check if this book is requested by curreny logged-in user or other user
                if borrow_book_exist_obj.student == request.user:
                    message = "You already requested this book from library, Please choose another book!!!"
                    return Response(get_formatted_response(200, message))
                else:
                    message = "This book is already requested by other student, Please try with other book!!!"
                    return Response(get_formatted_response(200, message))

        # If all the above conditions satisfied then create new request for borrow book request
        new_book_issue_payload = {
            "student": request.user,
            "book": book_obj,
            "book_application_date": datetime.datetime.today().date(),
        }

        try:
            # Set the current request user as book borrower and book instance
            book_borrow_request_obj = BookBorrower(**new_book_issue_payload)
            book_borrow_request_obj.save()
            message = "New book request successfully submitted, Librarian will approve your request shortly"
            return Response(
                get_formatted_response(
                    200, message, BookBorrowerSerializer(book_borrow_request_obj).data
                )
            )
        except Exception as e:
            message = (
                "Something went wrong while submitting new book request from library!!!"
            )
            return Response(get_formatted_response(400, message))

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class ApproveBorrowRequestView(generics.GenericAPIView):

    """
    POST: Approve borrow book request API

    :param:
        - id:
            - ID of that book-borrowe which you want to approve the book request as Librarian

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = BookBorrower.objects.all()
    serializer_class = BookBorrowerSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Get the book-borrower instance to view particular book ID/PK
        """
        obj = get_object_or_404(BookBorrower, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        """
        POST: Approve borrow book request API

        - Approve the book request by Librarian
        - Check with different conditions
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if currently logged-in user has profile or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # As of now only Librarian has permission to approve the borrow book request
        # So check the condition like logged-in user is librarian or member?
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to Approve Book Borrow Request!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            # If all the conditions are full-filled then get the book-borrow object
            # Change the details like book-issuer, book-status, total_books_due by student/member
            # Save the details
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
            message = (
                "Something went wrong while submitting new book request from library!!!"
            )
            return Response(get_formatted_response(400, message))

        issue_book_payload = {
            "book_issue_date": datetime.datetime.today().date(),
        }

        message = "Something went wrong!!!"
        return Response(get_formatted_response(400, message))


class ReturnBorrowBookView(APIView):

    """
    POST: Returns the book to library API

    :param:
        - id:
            - ID of that book which you want to return to library

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Get the book instance to view particular book ID/PK
        """
        obj = get_object_or_404(Book, id=self.kwargs["pk"])
        return obj

    def post(self, request, pk, *args, **kwargs):
        """
        POST: Returns the book to library API

        - Return the book to library
        - Check with different conditions
        """

        # Check if user is exist in request or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if currently logged-in user has profile or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            # Get the book
            book_obj = self.get_object()
        except Exception as e:
            message = (
                "Requested book is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check book exist in borrowed table or not?
        book_borrow_exist = BookBorrower.objects.filter(book=book_obj)

        if not book_borrow_exist.exists():
            message = "This book is not borrowed, So you can't return this book!!!"
            return Response(get_formatted_response(200, message, {}))
        else:
            borrow_book_exist_obj = book_borrow_exist.first()

            # Only own borrowed book return permission
            # Check if borrow book instance studnet/member is different from logged-in user
            if borrow_book_exist_obj.student != request.user:
                message = "This book is borrowed by someone else, So you are not authorized user to return this book!!!"
                return Response(get_formatted_response(200, message))

            # If book is borrowed then return to library with details
            if borrow_book_exist_obj.is_book_issued:
                if borrow_book_exist_obj.student == request.user:
                    # Update the book details
                    borrow_book_exist_obj.is_book_issued = False
                    borrow_book_exist_obj.book_return_date = (
                        datetime.datetime.now().date()
                    )
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


class DeleteBookView(generics.GenericAPIView):

    """
    DELETE: Delete Book API

    :param:
        - id:
            - ID of that book which you want to delete from the system

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        - DELETE: Delete Book API

        - Delete the book from the system as Librarian user
        """

        # Check if user is exist in request or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check currently logged-in user is active or not?
        if not request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check currently logged-in user has profile or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Delete book operation perform only by Librarian user so check the user permission
        # If current logged-in user is member then raise the error message
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to Delete Book!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user and self.kwargs.get("pk"):
            try:
                # Fetch the book object and delete from the system
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


class MyBorrowedBookList(generics.ListAPIView):

    """
    GET: List out all the borrowed by self/me/current logged-in user

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        """
        - Filter all the borrowed book by currently logged-in user
        """
        return Book.objects.filter(
            id__in=BookBorrower.objects.filter(student=self.request.user).values_list(
                "book", flat=True
            )
        )

    def get(self, request, *args, **kwargs):
        """
        - GET: List out all the borrowed by self/me/current logged-in user

        - Get all the books borrwed by the logged-in user
        """

        # Check if the user is exist or not in request?
        if self.request and not self.request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message))

        # Check if currently logged-in user is active or not?
        if not self.request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message))

        # Check if currently logged-in user has profile or not?
        if not hasattr(self.request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message))

        try:
            # Get all the list of borrowed books by currently logged-in user
            resp = self.list(request, *args, **kwargs)
            message = "Fetched my all borrowed book details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = (
                "Something went wrong while fetching my all borrowed book details!!!"
            )
            return Response(get_formatted_response(400, message, {}))


class AllPendingApprovalBookListView(generics.ListAPIView):

    """
    GET: All the pending book borrowee approval request

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = BookBorrower.objects.all()
    serializer_class = BookBorrowerSerializer

    def get_queryset(self):
        """
        - Filter all the borrowed book whoes user is null and is_book_issued is False
        - To get all the not approved book borrow list
        """
        return BookBorrower.objects.filter(
            book_issuer__isnull=True, is_book_issued=False
        )

    def get(self, request, *args, **kwargs):
        """
        - GET: All the pending book borrowee approval request

        - Get/Fetch all the pending approval book borrow request
        - Check all the possible conditions
        - This operation perform only by the librarian so check the user permission
        """

        # Check user is exist or not in request?
        if self.request and not self.request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message))

        # Check if currently logged-in user is active or not?
        if not self.request.user.is_active:
            message = "Your account is not activated yet, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message))

        # Check if currently logged-in user has profile or not?
        if not hasattr(self.request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message))

        # This operation perform only by Librarian user so check the user role permission
        # Check if currently logged-in user is Member then raise the error
        if (
            self.request.user.profile.is_member
            and not self.request.user.profile.is_librarian
        ):
            message = "As You are Logged-in as Member User, you are not authorized user to see pending approval requests!!!"
            return Response(get_formatted_response(200, message))

        try:
            # Filter all the pending approval book borrower lists or objects
            resp = self.list(request, *args, **kwargs)
            message = "Fetched details of pending book borrow details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = (
                "Something went wrong while fetching pending book borrow details!!!"
            )
            return Response(get_formatted_response(400, message, {}))
