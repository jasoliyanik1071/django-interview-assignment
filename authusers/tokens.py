# -*- coding: utf-8 -*-
"""
    - Common file to generate account activation or password rest link
"""
from __future__ import unicode_literals

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    - Account activation link generator class
    """

    def _make_hash_value(self, user, timestamp):
        """
        - Generate hash value for account activation link
        """
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(
            user.is_active
        )


account_activation_token = AccountActivationTokenGenerator()


class PasswordTokenGenerator(PasswordResetTokenGenerator):
    """
    - Account Password reset link generator class
    """

    def _make_hash_value(self, user, timestamp):
        """
        - Generate hash value for password reset link
        """
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(
            user.password
        )


password_reset_token = PasswordTokenGenerator()
