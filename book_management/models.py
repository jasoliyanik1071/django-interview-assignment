from django.db import models

from django.contrib.auth.models import User


BOOK_STATUS_CHOICES = (
    ("book_borrow", "Book BORROWED"),
    ("book_available", "Book AVAILABLE"),
)

class BookPublisher(models.Model):

    name = models.CharField(max_length=256)
    def __str__(self):
        """
            __str__ method is used to override default string returnd by an object
        """
        return self.name


class BookAuthor(models.Model):

    name = models.CharField(max_length=256)
    def __str__(self):
        """
            __str__ method is used to override default string returnd by an object
        """
        return self.name


class Book(models.Model):

    title = models.CharField("Title", max_length=256)
    subtitle = models.CharField("Sub Title", max_length=1024, null=True, blank=True)
    summary = models.TextField("Book Summary", max_length=1024, help_text="Enter a brief description of the book")
    isbn = models.CharField("ISBN", max_length=13, null=True, blank=True, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    author = models.ForeignKey(BookAuthor, null=True, blank=True, on_delete=models.CASCADE)
    publisher = models.ForeignKey(BookPublisher, null=True, blank=True, on_delete=models.CASCADE)

    publish_year = models.CharField("Book Publish Year", max_length=256, null=True, blank=True)

    # available_copies = models.IntegerField("Book Available Copy", default=0)

    book_status = models.CharField(max_length=36, choices=BOOK_STATUS_CHOICES, default="book_available")

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        """
            __str__ method is used to override default string returnd by an object
        """
        return self.title


class BookBorrower(models.Model):
    """
        IssuedBook
    """

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_application_date = models.DateField("Book Application Date", null=True,blank=True, help_text="Used to store new book application date")
    book_issue_date = models.DateField("Book Issue Date", null=True,blank=True, help_text="Used to store book issue date")
    book_return_date = models.DateField("Book Return Date", null=True,blank=True, help_text="Used to store book return date")

    is_book_issued = models.BooleanField("Is book issued?", default=False)

    book_issuer = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="book_issuer")

    def __str__(self):
        return self.student.username + " borrowed " + self.book.title
