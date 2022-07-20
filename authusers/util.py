# -*- coding: utf-8 -*-
"""
    - Common file for utils functionality which are used in whole website/API
"""

import logging

# 3rd party app imports
from rest_framework import exceptions, serializers
from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

log = logging.getLogger(__name__)


def get_current_site(request):
    """
    - This function calls when needs current site URL
    - As of now this is only used for sending activation email time host URL
    - It returns with site URL
    """
    if request.is_secure():
        site = "https://" + request.META["HTTP_HOST"]
    else:
        site = "http://" + request.META["HTTP_HOST"]
    return site


def get_formatted_response(status, message, data={}):
    """
    - It used for managing common API response
    - Each API returns with some response either its success or fails
    - To manage common structure of API response and easy to manage from mobile side developer
    - This will used in large scale application
    """
    return {"status": status, "message": message, "data": data}


class JSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    - Override the JWT token authentication for custom validations
    """

    def get_jwt_value(self, request):
        """
        - Override the "get_jwt_value" method
        - Check the token is exists in every API of call or not?
        - If not then return with token invalid or missing error
        - If token exist but not linked with any profile then raise error with token not match
        - If token match then authenticate user using that token and return with token
        """
        res = super(JSONWebTokenAuthentication, self).get_jwt_value(request)
        if res:
            print("Override JWT")
            token = res.decode()
            try:
                get_dict = VerifyJSONWebTokenSerializer().validate({"token": token})
                log.info(get_dict)
                if get_dict["user"].profile.jwt_token != token:
                    raise serializers.ValidationError(
                        "Token did'nt matched with that of user's !"
                    )
            except serializers.ValidationError as e:
                print(e)
                msg = "Invalid token"
                status = 401
                data = {}
                raise exceptions.AuthenticationFailed(
                    get_formatted_response(status, msg, data)
                )
        else:
            auth = get_authorization_header(request).split()
            if len(auth) == 0:
                msg = "Token not found"
                status = 401
                data = {}
                raise exceptions.AuthenticationFailed(
                    get_formatted_response(status, msg, data)
                )
        return res
