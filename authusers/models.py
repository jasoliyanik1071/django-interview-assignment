# -*- coding: utf-8 -*-
"""
    - Used to manage DataBase level models/tables
    - i.e:
        - We can create custom tables with pre-defined architecture
        - We can override the defult or existing tables
"""
from __future__ import unicode_literals

import logging

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Default imports
from django.db import models

# USER_ROLE_CHOICES = (
#     ("is_librarian", "LIBRARIAN"),
#     ("is_member", "MEMBER"),
# )

# As of now considering the app allows only below regex pattern for mobile as validation
mobile_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

log = logging.getLogger(__name__)


class Branch(models.Model):
    """
    - Used to manage Branch
    - i.e:
        - In future is required for student identification using category like branch
        - We can linked every student with particular branch for future reference

    # Fields:
        name:
            - Store the value of branch name or name of the branch
    """

    name = models.CharField("Branch Name", max_length=256)

    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.name


class UserProfile(models.Model):
    """
    - Used to manage users related its profiles
    - Django default provide user table and we can used the same but to avoid direct that table management I will use profile
    - Means if in future if its having too many fields then to avoide direct user table manipulate we can consider profile
    - This reference same as used in other applications
    - Means they can't change user itself but change its relavent profile reference
    - Might be I was wrong but I think it will helpfull for managing Users

    ## Use:
        - While creating any new user instance/object/record will create related profile and linked with user

    ## Fields:
    1). User:
        - After creating user linked with profile
    2). jwt_token:
        - To save JWT token after login API
        - To protect API with security protection will stored with profile and for authentication will use this token
        - Every API will check this token is valid or not and other stuff for security

    * To check user role is Librarin or Member take this 2 fields (is_librarina & is_member)
    * I take boolean field because its possible like user is work as librarian and can as member
    * So both fields are Ture if user is Librarian & Member
    3). is_librarian:
        - To identify user is librarian
    4). is_member:
        - To identify user is member
    5). created_by:
        - This field is used to store the record created user object
        - Means here in our functionality librarian can manage members menas able to create member user
        - So, if in future for identification like who created this member recrod to its easy to identify
    6). branch:
        - Used to store the branch of the member
        - Currently there is no use-case of this field
        - In future if its required to bifurcate the user according to stream then usefull
    7). roll_no:
        - Used to store the roll-numner or enrollment number of the member or student who is newly register
        - As of now dynamically created the records according to users details
        - As of now roll-number follow this pattern
        - i.e:
            - User's name first 2 character(Uppder Case) + Current year + User ID(Fill with 5 digit)
            - Means, User-Name is John Doe, Current Year is 2022, User ID is 1
            - Roll Number = JO202200001
    8). total_books_due:
        - Used to store total number of borrowed book by particular user
        - As of now the is no use-case in our but it will used for future
        - Means to generate library Analytics report
    9). mobile:
        - Used to store student mobile
        - Currently the is no use-case but in future if required then we can use this
    10). first_name:
        - Used to store student first-name
        - Currently the is no use-case but in future if required then we can use this
    11). last_name:
        - Used to store student last-name
        - Currently the is no use-case but in future if required then we can use this
    """

    user = models.OneToOneField(
        User,
        unique=True,
        db_index=True,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    jwt_token = models.CharField(max_length=1024, null=True, blank=True)

    # Below fields are used for Update details
    mobile = models.CharField(
        "Mobile Number", max_length=15, validators=[mobile_regex], blank=True, null=True
    )
    first_name = models.CharField("First Name", max_length=1000, blank=True, null=True)
    last_name = models.CharField("Last Name", max_length=1000, blank=True, null=True)

    # Below fields are used to store basic details required for library
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=36, null=True, blank=True)
    total_books_due = models.PositiveIntegerField(default=0)

    # Below fields are used to store role/permission bifurcation to the end/system user
    is_librarian = models.BooleanField("Is a Librarian?", default=False)
    is_member = models.BooleanField("Is a Member?", default=False)

    # This fields used to identify that who created the records
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )

    #
    def __str__(self):
        """
        __str__ method is used to override default string returnd by an object
        """
        return self.user.username if self.user and self.user.username else "-"

    @classmethod
    def login_validation(self, user, password, success):
        """
        - This method is call at the time of User Login API
        - This will check if user profile is exists or not?
            - If not then raise the error
        - This will check if the user is activate means registered properly or not?
            - If not then raise the error
        - This will also check if entered login details are incorrect or not?
            - If not then raise the error

        # Params:
            A. User:
                - User object
            B. Password:
                - Requested Password
            C. Success:
                - Flag to manage the status
        """
        message = []

        # To check if user profile is exist or not?
        if not hasattr(user, "profile"):
            message.append("Your profile is incomplete.")
        elif user.is_active:
            # To check if user is activated or not? and if yes then authenticate the requested params
            user = authenticate(username=user.username, password=password)
            if user is not None:
                # If user properly authenticated then return with success
                log.info("Login success - {} ({})".format(user.username, user.email))
                success = True
            else:
                # If having trouble then return with error message
                message.append("Incorrect Password.")
        else:
            # If profile or user account is not properly activated/completed
            message.append(
                "Please complete your pending activation by verifying Email!!!"
            )
        return message, success, user
