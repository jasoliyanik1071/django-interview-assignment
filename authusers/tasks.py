# -*- coding: utf-8 -*-
"""
    - Right now I will not consider this method in Celery but in future to manage user concarrency it will helpful
"""
from __future__ import unicode_literals

import logging

# Default Django imports
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def send_registration_email(site, username, email, activation_url):
    """
    - Call when all the details are correct and create new user object
    - Contains the user activation URL
    """
    mail_from = getattr(settings, "EMAIL_HOST_USER", "")

    subject = "Welcome to {platformname}, {new_user_name}".format(
        platformname=settings.PLATFORM_NAME, new_user_name=username
    )
    body = render_to_string(
        "lms/emails/user_registration_email.html",
        {
            "username": username,
            "site": site,
            "activation_url": activation_url,
            "settings": settings,
        },
    )

    try:
        send_mail(
            subject, "", mail_from, [email], html_message=body, fail_silently=False
        )
        log.info(
            "Activation Email has been sent to User {user_email}".format(
                user_email=email
            )
        )
    except Exception as error:
        log.error(
            "Error while sending activation email. {error}".format(error=str(error))
        )
