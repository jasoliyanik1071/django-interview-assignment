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

from authusers.serializers import UserSerializer, UserProfileSerializer, UserDetailSerializer
from authusers.models import UserProfile, Branch
from authusers.util import get_current_site, get_formatted_response, JSONWebTokenAuthentication

from authusers.tokens import account_activation_token, password_reset_token
from authusers.tasks import send_registration_email


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

log = logging.getLogger(__name__)


def index(request):
    context = {
        "user": request.user if request.user else False
    }
    return render(request, "lms/index.html", context)


class ActivateRegisteredUser(View):

    def render_template(self, template_path, context=dict()):
        """
            renders template
        """
        context.update({})
        return render(self.request, template_path, context)

    def get(self, request, uidb64, token):
        """
        """
        context = {}

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            import traceback
            log.exception(traceback.print_exc())

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            django_login(request, user)
            context = {
                "valid_activation": True
            }
            return self.render_template(template_path="lms/account_activation/activate.html", context=context)
        else:
            context = {
                "valid_activation": False
            }
            return self.render_template(template_path="lms/account_activation/activate.html", context=context)

        return self.render_template(template_path="lms/index.html", context=context)


def generic_user_creation(request, serializer, user_type):
    new_user = serializer.save()

    user_profile_payload = {
        "user": new_user,
    }
    request_payload = request.data.dict()
    username = request_payload.pop("username")
    password = request_payload.pop("password")
    email = request_payload.pop("email")
    user_profile_payload.update(request_payload)
 
    if request and request.user and not request.user.is_anonymous:
        user_profile_payload.update({
            "created_by": request.user
        })
    
    branch_obj = False
    if "branch_id" in request_payload and request_payload.get("branch_id"):
        branch_obj = Branch.objects.filter(id=request_payload.get("branch_id"))
        if branch_obj:
            user_profile_payload.update({
                "branch": branch_obj.first()
            })

    if user_type == "librarian":
        user_profile_payload.update({
            "is_librarian": True
        })
        userprofile_obj = UserProfile(**user_profile_payload)
    else:
        user_profile_payload.update({
            "is_member": True
        })
        userprofile_obj = UserProfile(**user_profile_payload)

    curr_year = datetime.datetime.now().year
    if branch_obj:
        roll_number = branch_obj.first().name[:2].upper() + username[:2].upper() + str(curr_year) + str(userprofile_obj.id).zfill(5)
    else:
        roll_number = username[:2].upper() + str(curr_year) + str(userprofile_obj.id).zfill(5)

    userprofile_obj.roll_no = roll_number
    userprofile_obj.save()

    if request_payload.get("first_name"):
        userprofile_obj.user.first_name = request_payload.get("first_name")
    if request_payload.get("last_name"):
        userprofile_obj.user.last_name = request_payload.get("last_name")
    userprofile_obj.user.save()

    site = get_current_site(request)

    uid = urlsafe_base64_encode(force_bytes(new_user.pk))
    token = account_activation_token.make_token(new_user)
    activation_url = site + reverse("authusers:useractivation", kwargs={"uidb64": uid, "token": token})

    send_registration_email(
        site=site,
        username=new_user.username,
        email=new_user.email,
        activation_url=activation_url
    )

    log.info("{platform_name} account created for user {username}".format(platform_name=settings.PLATFORM_NAME, username=new_user.username))

    message = "User created successfully and Email has been sent. So please activate account using activation link in mail."
    log.info("User registered successfully")
    # status = 200

    data = get_formatted_response(status.HTTP_201_CREATED, message, serializer.data)

    if data and "data" in data:
        data["data"].update({
            "activation_url": activation_url
        })
    return data


@authentication_classes([])
@permission_classes([])
class LibrarianRegisterView(APIView):
    """
        - Librarian Register View
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "librarian"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([])
class MemberRegisterView(APIView):
    """
        - Member Register View
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "member"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JSONWebTokenAPIOverride(ObtainJSONWebToken):
    """
    Override JWT
    """
    user_serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if request.data:
            username = request.data["username"]
            password = request.data["password"]

            if not username:
                return Response(get_formatted_response(
                    404,
                    "Username is missing"
                ))

            if not password:
                return Response(get_formatted_response(
                    404,
                    "Password is missing"
                ))

            user = User.objects.filter(username=username).first()

            if not user:
                message = "Account with this username does not exists"
                return Response(get_formatted_response(
                    404,
                    message
                ))

            if not user.check_password(password):
                raise AuthenticationFailed("Incorrect Password!!!")


            if user and not hasattr(user, "profile"):
                message = "UserProfile not exist, Please contect Administrator!!!"
                return Response(get_formatted_response(
                    404,
                    message
                ))

            if user and not user.is_active:
                message = "Your account is not verified yet, Please contect Administrator!!!"
                return Response(get_formatted_response(
                    404,
                    message
                ))

            data = request.data
            token = data.get("access_token")
            username = data.get("username")

            response = super(JSONWebTokenAPIOverride, self).post(request, *args, **kwargs)

            if response:
                if response and response.status_code == status.HTTP_200_OK:
                    token = response.data.get('token')
                    user = User.objects.filter(username=request.data['username']).first()
                    # serialized_user = self.user_serializer_class(user)
                    # response.data.update(serialized_user.data)
                    response.data = {
                        "status": 200,
                        "message": "Login Successfully",
                        "data": {
                            "access_token": token,
                            "token": token,
                            "user_id": user.id,
                            "full_name": user.get_full_name(),
                            "email_id": user.email,
                        }
                    }
                    user.profile.jwt_token = token
                    user.profile.save()

                    user.save()
                else:
                    if response.data and response.data.get('non_field_errors'):
                        response.status_code = 200
                        response.data = {
                            "status": 404,
                            "message": str(response.data.get('non_field_errors')[0]),
                            "data": {}
                        }
                    else:
                        response.data = {
                            "status": 404,
                            "message": "Username and Password must not be empty",
                            "data": {}
                        }
                return response
            else:
                response = {
                    "status": 404,
                    "message": "Something wrong happened",
                    "data": {}
                }
                return Response(response)
        else:
            return Response(get_formatted_response(404, "Please enter proper data to login"))


class LogoutView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    def post(self, request):
        request.user.profile.jwt_token = ""
        request.user.profile.save()
        request.user.save()
        return Response(get_formatted_response(200, "User logged out successfully."))


class MemberRegisterByLibrarianView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "member"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUdateView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def get_object(self):
        if self.kwargs and "pk" in self.kwargs:
            if self.kwargs["pk"]:
                obj = get_object_or_404(User, id=self.kwargs["pk"])
            else:
                obj = self.request.user
        else:
            obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, You don't have rights to update another user account!!!"
            return Response(get_formatted_response(200, message, {}))

        if not instance.is_active:
            message = "The user which you trying to update his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        serializer = self.get_serializer(instance.profile, data=request.data, partial=True)

        if serializer.is_valid():
            updated_user_obj = serializer.save()

            if not updated_user_obj.roll_no:
                curr_year = datetime.datetime.now().year
                if updated_user_obj.branch:
                    roll_number = updated_user_obj.branch.name[:2].upper() + username[:2].upper() + str(curr_year) + str(userprofile_obj.id).zfill(5)
                else:
                    roll_number = username[:2].upper() + str(curr_year) + str(userprofile_obj.id).zfill(5)

                updated_user_obj.roll_no = roll_number
                updated_user_obj.save()

            message = "Profile updated successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def delete(self, request, pk, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user.id == pk and request.user.profile.is_librarian:
            message = "As You are Logged-in as Librarian User, User must not delete itself whichs currently Logged-in. Please login with different account!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user.id != pk and (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, You don't have rights to delete another user account!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user and pk:
            delete_request_user_obj = User.objects.filter(id=pk)

            if delete_request_user_obj and delete_request_user_obj.first():
                if (request.user.profile.is_member and not request.user.profile.is_librarian) and delete_request_user_obj.first().profile.is_librarian:
                    message = "As You are Logged-in as Member User, you are not authorized user to delete Librarian User Account!!!"
                    return Response(get_formatted_response(200, message, {}))

                try:
                    delete_request_user_obj.first().profile.delete()
                    delete_request_user_obj.first().delete()
                    message = "User & Profile Deleted successfully!!!"
                    return Response(get_formatted_response(200, message, {}))
                except Exception as e:
                    message = "Something went wrgon while deleting the user!!!"
                    return Response(get_formatted_response(400, message, {}))
            else:
                message = "Record does not exist in system, Something went wrgon while deleting the user!!!"
                return Response(get_formatted_response(400, message, {}))
        else:
            message = "Something went wrong, Please check the request data and then try again!!!"
            return Response(get_formatted_response(400, message, {}))


class MemberUserDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not request.user.is_active:
            message = "The user which you trying to delete his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user.profile.is_librarian:
            message = "As You are Logged-in as Librarian User, User must not delete itself whichs currently Logged-in. Please login with different account!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user:
            try:
                self.request.user.profile.delete()
                self.request.user.delete()
                message = "User & Profile Deleted successfully!!!"
                return Response(get_formatted_response(200, message, {}))
            except Exception as e:
                message = "Something went wrgon while deleting the user!!!"
                return Response(get_formatted_response(400, message, {}))
        else:
            message = "Something went wrong, Please check the request data and then try again!!!"
            return Response(get_formatted_response(400, message, {}))


class UserListView(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, you are not authorized user to access all the user details!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            resp = self.list(request, *args, **kwargs)
            message = "Fetched All Users Details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = "Something went wrong while fetching Users Details!!!"
            return Response(get_formatted_response(400, message, {}))


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = "pk"

    def get_object(self):
        if self.kwargs and "pk" in self.kwargs:
            if self.kwargs["pk"]:
                obj = get_object_or_404(User, id=self.kwargs["pk"])
            else:
                obj = self.request.user
        else:
            obj = self.request.user
        return obj

    def get(self, request, pk, *args, **kwargs):
        user_detail_obj = self.get_object()

        if not user_detail_obj.is_active:
            message = "The user which you trying to get Details his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        serializer = self.serializer_class(user_detail_obj)

        if request and not request.user:
            message = "User not exist in request, Please try once again with latest token!!!"
            return Response(get_formatted_response(200, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if (request.user.profile.is_member and not request.user.profile.is_librarian):
            message = "As You are Logged-in as Member User, you are not authorized user to access details of Librarian User Account!!!"
            return Response(get_formatted_response(200, message, {}))

        if serializer and self.kwargs["pk"]:
            message = "Fetch details successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
