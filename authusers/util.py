# -*- coding: utf-8 -*-

import logging

from rest_framework import exceptions, serializers
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework.authentication import get_authorization_header


log = logging.getLogger(__name__)


def get_current_site(request):
    if request.is_secure():
        site = "https://" + request.META['HTTP_HOST']
    else:
        site = "http://" + request.META['HTTP_HOST']
    return site

def get_formatted_response(status, message, data={}):
    return {
        "status": status,
        "message": message,
        "data": data
    }


class JSONWebTokenAuthentication(JSONWebTokenAuthentication):

    def get_jwt_value(self, request):
        res = super(JSONWebTokenAuthentication, self).get_jwt_value(request)
        if res:
            print("Override JWT")
            token = res.decode()
            try:
                get_dict = VerifyJSONWebTokenSerializer().validate({'token': token})
                log.info(get_dict)
                if get_dict['user'].profile.jwt_token != token:
                    raise serializers.ValidationError("Token did'nt matched with that of user's !")
            except serializers.ValidationError as e:
                print(e)
                msg = "Invalid token"
                status = 401
                data = {}
                raise exceptions.AuthenticationFailed(get_formatted_response(status, msg, data))
        else:
            auth = get_authorization_header(request).split()
            if len(auth) == 0:
                msg = "Token not found"
                status = 401
                data = {}
                raise exceptions.AuthenticationFailed(get_formatted_response(status, msg, data))
        return res
