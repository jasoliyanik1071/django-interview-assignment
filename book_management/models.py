# -*- coding: utf-8 -*-
"""
    - Used to manage DataBase level models/tables
    - i.e:
        - We can create custom tables with pre-defined architecture
        - We can override the defult or existing tables
"""

# Default Django imports
from django.contrib.auth.models import User
from django.db import models

BOOK_STATUS_CHOICES = (
    ("book_borrow", "Book BORROWED"),
    ("book_available", "Book AVAILABLE"),
)


class BookPublisher(models.Model):
    """
    - Used to manage Book-Publisher

    # Fields:
    name:
        - Store the value of Book-Publisher or name of the Book-Publisher
    """

    name = models.CharField(max_length=256)

    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.name


class BookAuthor(models.Model):
    """
    - Used to manage Book-Author

    # Fields:
    name:
        - Store the value of Book-Author or name of the Book-Author
    """

    name = models.CharField(max_length=256)

    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.name


class Book(models.Model):
    """
    - Used to manage book in library

    # Fields:
        title:
            - Used to store title of the book
        subtitle:
            - Used to store subtile of the book
        summary:
            - Used to store shory summary about the book
        isbn:
            - Used to store ISBN value of the book
            - In future it will helpful to search book
        author:
            - Used to store the author of the book or owner of the book
        publisher:
            - Used to store book publisher
        publish_year:
            - Used to store book published year
        book_status:
            - Used to store book status
            - As of now will only consider single copy/copies of the book
            - So when every any student borrowed the book then book status goes into Borrowed
            - Once the book is return then status is Available
        created_by:
            - Store the record created user for future reference purpose
    """

    title = models.CharField("Title", max_length=256)
    subtitle = models.CharField("Sub Title", max_length=1024, null=True, blank=True)
    summary = models.TextField(
        "Book Summary",
        max_length=1024,
        help_text="Enter a brief description of the book",
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        null=True,
        blank=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )

    author = models.ForeignKey(
        BookAuthor, null=True, blank=True, on_delete=models.CASCADE
    )
    publisher = models.ForeignKey(
        BookPublisher, null=True, blank=True, on_delete=models.CASCADE
    )

    publish_year = models.CharField(
        "Book Publish Year", max_length=256, null=True, blank=True
    )

    # available_copies = models.IntegerField("Book Available Copy", default=0)

    book_status = models.CharField(
        max_length=36, choices=BOOK_STATUS_CHOICES, default="book_available"
    )

    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.title


class BookBorrower(models.Model):
    """
    - Used to manage book borrower management for library or librarian purpose

    Management:
        - This table manage in 3 stage:
        A. Request for book by Student/Member
        B. Check and approve the book borrow request by Librarian
        C. Return the book to library by Student/Member

    Usage A:
        - Whenever any student request for any book then I create record on this table with basic details
        - i.e:
            - Once Student/Member request for any book then check if book is avilable or not?
            - If YES:
                - Create record with Student(Who is user), Book(Which book want to borrow)
            - If NO:
                - Return with error message like book is borrowed by someone else

    Usage B:
        - Librarian check all the borrower request and approve the request
        - Once approve the request then change the book status to borrowed

    Usage C:
        - Member/Student request for book return and now book status change to available

    # Fields:
        student:
            - Store the member/student object
        book:
            - Store the book reference against student/member
        book_issue_data:
            - Store the book issue date
        book_return_date:
            - Store the book return date
        is_book_issued:
            - True if book is assign to student/member
        book_issuer:
            - Store the Book issuer reference
    """

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_application_date = models.DateField(
        "Book Application Date",
        null=True,
        blank=True,
        help_text="Used to store new book application date",
    )
    book_issue_date = models.DateField(
        "Book Issue Date",
        null=True,
        blank=True,
        help_text="Used to store book issue date",
    )
    book_return_date = models.DateField(
        "Book Return Date",
        null=True,
        blank=True,
        help_text="Used to store book return date",
    )

    is_book_issued = models.BooleanField("Is book issued?", default=False)

    book_issuer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="book_issuer",
    )

    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.student.username + " borrowed " + self.book.title
