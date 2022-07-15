# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models
from django.contrib.auth import authenticate, login as django_login

from django.contrib.auth.models import User

from django.core.validators import RegexValidator

# USER_ROLE_CHOICES = (
#     ("is_librarian", "LIBRARIAN"),
#     ("is_member", "MEMBER"),
# )

mobile_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

log = logging.getLogger(__name__)


class Branch(models.Model):
    name = models.CharField("Branch Name", max_length=256)

    def __str__(self):
        """
            __str__ method is used to override default string returnd by an object
        """
        return self.name

class UserProfile(models.Model):
    """
        docstring for CustomUser
    """
    user = models.OneToOneField(User, unique=True, db_index=True, related_name="profile", on_delete=models.CASCADE)
    jwt_token = models.CharField(max_length=1024, null=True, blank=True)

    # 
    is_librarian = models.BooleanField("Is a Librarian?", default=False)
    is_member = models.BooleanField("Is a Member?", default=False)

    # 
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    # 
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=36, null=True, blank=True)
    total_books_due = models.PositiveIntegerField(default=0)


    # Below details are used for Update details
    mobile = models.CharField("Mobile Number", max_length=15, validators=[mobile_regex], blank=True, null=True)
    first_name = models.CharField("First Name", max_length=1000, blank=True, null=True)
    last_name = models.CharField("Last Name", max_length=1000, blank=True, null=True)


    def __str__(self):
        return self.user.username if self.user and self.user.username else "-"

    @classmethod
    def login_validation(self, user, password, success):
        message = []

        if not hasattr(user, 'profile'):
            message.append("Your profile is incomplete.")
        elif user.is_active:
            user = authenticate(username=user.username, password=password)
            if user is not None:
                # django_login(request, user)
                log.info('Login success - {} ({})'.format(user.username, user.email))
                success = True
            else:
                message.append("Incorrect Password.")
        else:
            message.append("Please complete your pending activation by verifying Email!!!")
        return message, success, user
