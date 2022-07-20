# -*- coding: utf-8 -*-
"""
    - Business logic for users management API's
    - All the APIs related to Users is manage in this file

    - i.e:
        01). Register Librarian (Library Head who manage the books from the library)
            - LibrarianRegisterView

        02). Register Member (Library students who used the books)
            - MemberRegisterView

        03). Register Member using Librarian User (Librarian able to create Member user registration)
            - MemberRegisterByLibrarianView

        04). User Account Verification - After Registration
            - ActivateRegisteredUser

        05). User Login (As Librarian or Member)
            - JSONWebTokenAPIOverride

        06). Update User (As Librarian able to update Member users details)
            - UserUpdateView

        07). Update User (As Librarian/Member able to update users details)
            - UserUpdateView

        08). Delete User (As Librarian able to delete Member users from the system)
            - UserDeleteView
            
        09). Delete User (As Member able to delete own account from the system)
            - MemberUserDeleteView

        10). List of all Users (As Librarian user able to get all the system users details)
            - UserListView

        11). Particular User Detail (As Librarian user able to get specific users details from the system)
            - UserDetailView

        12). User Logout
            - LogoutView

        13). index method:
            - After activate the account redirect to home page created index function
"""
from __future__ import unicode_literals

import datetime
import logging

# Default Django imports
from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

# 3rd party Rest-Framework imports
from rest_framework import generics, mixins, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# 3rd party REST-JWT imports
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken

# Custom App (AuthUsers) imports
from authusers.models import Branch, UserProfile
from authusers.serializers import (
    UserDetailSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from authusers.tasks import send_registration_email
from authusers.tokens import account_activation_token
from authusers.util import (
    JSONWebTokenAuthentication,
    get_current_site,
    get_formatted_response,
)

# Logger define
log = logging.getLogger(__name__)


def index(request):

    """
    - Index/Home page of the website
    - As of now there is only used to render homepage after activate the users account
    - i.e:
        - When user gets account activation email with link and users click on that link thne account gets verified but
        - To return homepage used this function/method
    """
    context = {"user": request.user if request.user else False}
    return render(request, "lms/index.html", context)


def generic_user_creation(request, serializer, user_type):

    """
    - This method is common method which manage the user creation flow
    - As of now this method calls in 3 cases:
        A. When Register as Librarian User
        B. When Register as Member User
        C. When Register Member as Librarian User

    # Params:
        A. request:
            - Request object of the API
        B. serializer:
            - Current request related "serializer" object
        C. user_type:
            - Requested user-type as either "librarian" or "member"
            - "librarian":
                - If requested as Librarian user registration
            - "member":
                - If requested as Member user registration OR
                - If Librarian request for new Member registration

    A. If as Librarian:
        - user_type = "librarian"
    B. If as Member:
        - user_type = "member"
    C. If register Member using Librarian User:
        - user_type = "member"
    """

    # Save the user-serializer object
    new_user = serializer.save()

    # Common payload dictionary to create its profile record
    user_profile_payload = {
        "user": new_user,
    }

    request_payload = request.data.dict()
    username = request_payload.pop("username")
    password = request_payload.pop("password")
    email = request_payload.pop("email")
    user_profile_payload.update(request_payload)

    # Will check if request.user is exist and if user is not anonymous user
    # If all the details are correct then will set created_by as requested user object
    # For identify that who created this member account
    if request and request.user and not request.user.is_anonymous:
        user_profile_payload.update({"created_by": request.user})

    # Set the branch if it exist in request payload
    branch_obj = False
    if "branch_id" in request_payload and request_payload.get("branch_id"):
        branch_obj = Branch.objects.filter(id=request_payload.get("branch_id"))
        if branch_obj:
            user_profile_payload.update({"branch": branch_obj.first()})

    # Set the user type according to user-type value
    if user_type == "librarian":
        user_profile_payload.update({"is_librarian": True})
        userprofile_obj = UserProfile(**user_profile_payload)
    else:
        user_profile_payload.update({"is_member": True})
        userprofile_obj = UserProfile(**user_profile_payload)

    # Dynamically generate the roll-number value and set it to profile object
    # Roll number is combination of branch, username, current year and user ID
    # i.e:
    # roll_no = username first 2 letter + current year + user id (fill with 5 digit)
    # Save the roll_no value to user-profile
    curr_year = datetime.datetime.now().year
    roll_number = (
        username[:2].upper() + str(curr_year) + str(userprofile_obj.id).zfill(5)
    )
    userprofile_obj.roll_no = roll_number
    userprofile_obj.save()

    # If first-name is exist in request payload then update it to user object
    if request_payload.get("first_name"):
        userprofile_obj.user.first_name = request_payload.get("first_name")

    # If last-name is exist in request payload then update it to user object
    if request_payload.get("last_name"):
        userprofile_obj.user.last_name = request_payload.get("last_name")
    # Save the user object
    userprofile_obj.user.save()

    # ==========================================================================
    #               Sending the Account activation E-Mail
    # ==========================================================================
    # Get the current site
    site = get_current_site(request)

    # Encode the user-ID
    uid = urlsafe_base64_encode(force_bytes(new_user.pk))

    # Generate the token with user object
    token = account_activation_token.make_token(new_user)

    # Generate the hash URL
    activation_url = site + reverse(
        "authusers:useractivation", kwargs={"uidb64": uid, "token": token}
    )

    # Created common function to send email
    # Pass the required params to the function
    send_registration_email(
        site=site,
        username=new_user.username,
        email=new_user.email,
        activation_url=activation_url,
    )
    log.info(
        "{platform_name} account created for user {username}".format(
            platform_name=settings.PLATFORM_NAME, username=new_user.username
        )
    )

    message = "User created successfully and Email has been sent. So please activate account using activation link in mail."
    log.info("User registered successfully")

    # Get the common API response format
    data = get_formatted_response(status.HTTP_201_CREATED, message, serializer.data)

    if data and "data" in data:
        data["data"].update({"activation_url": activation_url})
    return data


@authentication_classes([])
@permission_classes([])
class LibrarianRegisterView(generics.GenericAPIView):

    """
    POST: Librarian Register API

    :param:
        - email:
            - Email of user and to send account vefirication account it used
        - username:
            - Username of the user
        - password:
            - Password of the user
    :return:
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        """
        - POST: Librarian Register API

        - Get the request payload
        - Pass to User-Serializer
        - Validate the Serializer using default is_valid method
        - Return the response with Success or Fail payload
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "librarian"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([])
class MemberRegisterView(generics.GenericAPIView):

    """
    POST: Member Register API

    :param:
        - email:
            - Email of user and to send account vefirication account it used
        - username:
            - Username of the user
        - password:
            - Password of the user
    :return:
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        """
        - POST: Member Register API

        - Get the request payload
        - Pass to User-Serializer
        - Validate the Serializer using default is_valid method
        - Return the response with Success or Fail payload
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "member"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberRegisterByLibrarianView(generics.GenericAPIView):

    """
    POST: Member Register as Librarian User API

    :param:
        - email:
            - Email of user and to send account vefirication account it used
        - username:
            - Username of the user
        - password:
            - Password of the user
    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        """
        - POST: Member Register as Librarian User API

        - Get the request payload
        - Pass to User-Serializer
        - Validate the Serializer using default is_valid method
        - Return the response with Success or Fail payload

        - Check the below conditions if request as Librarian:
            A. If user is exist or not?
            B. Profile is exist or not for that request user
            C. Check requested user is Member or Librarian user
            D. Chek requested account is activated or not?
        """
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, You don't have rights to create member user account!!!"
            return Response(get_formatted_response(200, message, {}))

        if not instance.is_active:
            message = "The user which you trying to update his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = "member"
            data = generic_user_creation(request, serializer, user_type)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateRegisteredUser(View):

    """
    GET:
    - Custom class to manage account verification
    - Call when click on account vefirication URL
    - Activate the user account once user get the account verification email after successfully register
    """

    def render_template(self, template_path, context=dict()):
        """
        - renders template after clicking on account verification URL(link)
        """
        context.update({})
        return render(self.request, template_path, context)

    def get(self, request, uidb64, token):
        """
        - Check the account activation link is valid or not?
        - If account is already clicked means verified then return with failure message
            - i.e: This account is already verified
        - If account is not verified then activate that account and render success page and redirect to webpage
        """
        context = {}

        try:
            # Decode the activation url is valid or not?
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            import traceback

            log.exception(traceback.print_exc())

        # If decoded successfully and then check token is valid or not?
        if user is not None and account_activation_token.check_token(user, token):
            # If token is valid then set is-active = True and save the user instance/object
            # Then authenticate the request with user
            # Return with success page (Render the success page) with account verified success message
            user.is_active = True
            user.save()
            django_login(request, user)
            context = {"valid_activation": True}
            return self.render_template(
                template_path="lms/account_activation/activate.html", context=context
            )
        else:
            # If account is already verified then return with fail message like
            # This account is already verified
            context = {"valid_activation": False}
            return self.render_template(
                template_path="lms/account_activation/activate.html", context=context
            )

        # If something went wrong then return with homepage
        return self.render_template(template_path="lms/index.html", context=context)


class JSONWebTokenAPIOverride(ObtainJSONWebToken):

    """
    description: User Login API
    POST: User Login API

    parameters:
        - username:
            type: string
            required: true
            location: form
        - password:
            type: string
            required: true
            location: form
    :return:
    """

    user_serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        - POST: User Login API

        # Working Description:
        ======================
            - Check if all the params is exist or not for Login API

            - Check if username is exist in request with value
            - Check if password is exist in request with value

            - Check if user is exist or not in system

            - If password is exist in request and that is not belong with any system user account

            - If current user who is requesting has not profile exist

            - If current requested user is not activated
        """
        if request.data:
            username = request.data["username"]
            password = request.data["password"]

            # Check if username is exist or not in request
            if not username:
                return Response(get_formatted_response(404, "Username is missing"))

            # Check if password is exist or not in request
            if not password:
                return Response(get_formatted_response(404, "Password is missing"))

            # Filter user record from the system
            user = User.objects.filter(username=username).first()

            # Check if user record is not exit then raise the error
            if not user:
                message = "Account with this username does not exists"
                return Response(get_formatted_response(404, message))

            # Check if user exist but that requested password is not match with system user account
            if not user.check_password(password):
                raise AuthenticationFailed("Incorrect Password!!!")

            # Check profile is not exist
            if user and not hasattr(user, "profile"):
                message = "UserProfile not exist, Please contect Administrator!!!"
                return Response(get_formatted_response(404, message))

            # Check user is activated or not?
            if user and not user.is_active:
                message = (
                    "Your account is not verified yet, Please contect Administrator!!!"
                )
                return Response(get_formatted_response(404, message))

            # If all the details are correct
            data = request.data
            token = data.get("access_token")
            username = data.get("username")

            # Call the default method with super to validated with JWT and return with token and user object
            response = super(JSONWebTokenAPIOverride, self).post(
                request, *args, **kwargs
            )

            if response:
                # If response & status is OK then return with token and user object with JSON
                if response and response.status_code == status.HTTP_200_OK:
                    token = response.data.get("token")
                    user = User.objects.filter(
                        username=request.data["username"]
                    ).first()

                    response.data = {
                        "status": 200,
                        "message": "Login Successfully",
                        "data": {
                            "access_token": token,
                            "token": token,
                            "user_id": user.id,
                            "full_name": user.get_full_name(),
                            "email_id": user.email,
                        },
                    }
                    user.profile.jwt_token = token
                    user.profile.save()

                    user.save()
                else:
                    # Return with response
                    if response.data and response.data.get("non_field_errors"):
                        response.status_code = 200
                        response.data = {
                            "status": 404,
                            "message": str(response.data.get("non_field_errors")[0]),
                            "data": {},
                        }
                    else:
                        # Return with response
                        response.data = {
                            "status": 404,
                            "message": "Username and Password must not be empty",
                            "data": {},
                        }
                return response
            else:
                # Return with response
                response = {
                    "status": 404,
                    "message": "Something wrong happened",
                    "data": {},
                }
                return Response(response)
        else:
            # Return with response
            return Response(
                get_formatted_response(404, "Please enter proper data to login")
            )


class UserUpdateView(generics.GenericAPIView):
    """
    PUT: Update User Details API

    * This API call in 2 cases:
        1. Update Member details as Librarian User
            - If Librarian wants to update any account details then pass particular ID of that user
        2. Update Member details(As member or As Librarian)
            - Here in this case not pass any user ID because any account can pass self/own details

    Note:
        1. If update user details for own means as Librarian or as Member then get user from request
        2. If Librarian wants to update details for other member then pass that user ID and will fetch that ID from the request and update that particular records user details

    :param:
        - is_librarian:
            - Value as True if want to make user as Librarian role
        - is_member:
            - Value as True if want to make user as Member role
        - mobile:
            - Mobiile number of the user
        - first_name:
            - First name of the user
        - last_name:
            - Last name of the user
        - branch:
            - Branch ID of the student

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Default method
        - Will check if Librarian wants to update other user details or not?
            If YES:
                - Then will take the ID from the request and get the user object and return
            If NOL
                - Then will take the ID from the requested user and return requested user
        """
        if self.kwargs and "pk" in self.kwargs:
            if self.kwargs["pk"]:
                obj = get_object_or_404(User, id=self.kwargs["pk"])
            else:
                obj = self.request.user
        else:
            obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        """
        - PUT: Update User Details API

        - Default method of CBV
        - Will override this method and update the payload related data to requested users
        """
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        - This method used to manipulate the user details

        Working Mechenism:
            - Get the user object
            - Check the conditions like if the user is exist or not?
            - If user exist then profile exist or not?
            - If user exist then check is member or not? because as member not allow to update other account details
            - If user is active or not?

            - Serialize the requested data
            - Check if serialize data is valiid or not?
            - Save the updated data to user
            - if roll_no is not set then dynamically create and save
        """
        try:
            instance = self.get_object()
        except Exception as e:
            message = (
                "Requested user is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if request user is exist or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if profile is exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Check if "pk" means user ID is exist or not?
        # If exist then check if that request user is member or librarian
        # If member then raise error
        if "pk" in self.kwargs and self.kwargs["pk"]:
            if (
                request.user.id != self.kwargs["pk"]
                and request.user.profile.is_member
                and not request.user.profile.is_librarian
            ):
                message = "As You are Logged-in as Member User, You don't have rights to update another user account!!!"
                return Response(get_formatted_response(200, message, {}))

        # Check user is active or not?
        if not instance.is_active:
            message = "The user which you trying to update his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Serialize the request data for user
        serializer = self.get_serializer(
            instance.profile, data=request.data, partial=True
        )

        # Check validation of the requested data
        if serializer.is_valid():
            updated_user_obj = serializer.save()

            # If roll-no is not set then generate and save it
            if not updated_user_obj.roll_no:
                curr_year = datetime.datetime.now().year
                roll_number = (
                    username[:2].upper()
                    + str(curr_year)
                    + str(userprofile_obj.id).zfill(5)
                )

                updated_user_obj.roll_no = roll_number
                updated_user_obj.save()

            message = "Profile updated successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(generics.GenericAPIView):
    """
    DELETE: Delete User Account As Librarian

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

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def delete(self, request, pk, *args, **kwargs):
        """
        - DELETE: Delete User Account As Librarian

        - Check all the possible conditions before deleting the user from the system
        - Delete the account from the system as member or librarian or Member login as Librarian
        """
        # Check if user is exist in request or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if current logged-in user is active or not?
        if not request.user.is_active:
            message = "The user which you trying to delete his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if profile is exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Check if requested user ID and current login user are same and logged-in user is librarian then unable to delete own account
        if request.user.id == pk and request.user.profile.is_librarian:
            message = "As You are Logged-in as Librarian User, User must not delete itself whichs currently Logged-in. Please login with different account!!!"
            return Response(get_formatted_response(200, message, {}))

        # Check if requested user ID and current login ID is not same
        # If current logged-in user is member but not librarian then not able to delete any user details from the system
        if request.user.id != pk and (
            request.user.profile.is_member and not request.user.profile.is_librarian
        ):
            message = "As You are Logged-in as Member User, You don't have rights to delete another user account!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user and pk:
            # Check if record is exist or not?
            delete_request_user_obj = User.objects.filter(id=pk)

            # If record exist
            if delete_request_user_obj and delete_request_user_obj.first():
                # Check if requested user ID is belongs with librarian user
                # If requested user is member then
                # return with error message
                if (
                    request.user.profile.is_member
                    and not request.user.profile.is_librarian
                ) and delete_request_user_obj.first().profile.is_librarian:
                    message = "As You are Logged-in as Member User, you are not authorized user to delete Librarian User Account!!!"
                    return Response(get_formatted_response(200, message, {}))

                try:
                    # If all the conditions are full-filled then delete profile and linked account details from the system
                    delete_request_user_obj.first().profile.delete()
                    delete_request_user_obj.first().delete()
                    message = "User & Profile Deleted successfully!!!"
                    return Response(get_formatted_response(200, message, {}))
                except Exception as e:
                    # Error while deleting the user account
                    message = "Something went wrgon while deleting the user!!!"
                    return Response(get_formatted_response(400, message, {}))
            else:
                # Error while requested user ID for delete is no longer exist in system
                message = "Record does not exist in system, Something went wrgon while deleting the user!!!"
                return Response(get_formatted_response(400, message, {}))
        else:
            # if something happens wrong
            message = "Something went wrong, Please check the request data and then try again!!!"
            return Response(get_formatted_response(400, message, {}))


class MemberUserDeleteView(generics.GenericAPIView):
    """
    DELETE: Delete User Account(Self)

    - If any member wants to delete own account from the system then able to delete

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        - DELETE: Delete User Account(Self)

        - Check all the possible conditions before deleting the user from the system
        - Delete the account from the system as member or librarian or Member login as Librarian
        """
        # Check if user is exist in request or not?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if current logged-in user is active or not?
        if not request.user.is_active:
            message = "The user which you trying to delete his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if profile is exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # As of now only allows to delete member accounts
        # So check if currently logged-in user is as librarian or not?
        # If yes then raise the error
        if request.user.profile.is_librarian:
            message = "As You are Logged-in as Librarian User, User must not delete itself whichs currently Logged-in. Please login with different account!!!"
            return Response(get_formatted_response(200, message, {}))

        if request.user:
            try:
                # Delete the logged-in user profile and its linked user account from the system
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


class UserListView(generics.ListAPIView):
    """
    GET: All System Users List API
    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        - GET: All System Users List API

        - Fetch all the system users and its details
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if current logged-in user is active or not?
        if not request.user.is_active:
            message = "The user which you trying to delete his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Check if profile is exist or not in currently logged-in user?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Here member user not allow to get/fetch system user details so check condition for user role/permission
        # If currently logged-in user is as member then return with error message
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to access all the user details!!!"
            return Response(get_formatted_response(200, message, {}))

        try:
            # Fetch all the list of user with related details
            resp = self.list(request, *args, **kwargs)
            message = "Fetched All Users Details successfully!!!"
            return Response(get_formatted_response(200, message, resp.data))
        except Exception as e:
            message = "Something went wrong while fetching Users Details!!!"
            return Response(get_formatted_response(400, message, {}))


class UserDetailView(generics.GenericAPIView):
    """
    GET: Fetch the particular User Details API

    :param:
        - id:
            - ID of that account which you want to check details

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = "pk"

    def get_object(self):
        """
        - Default method
        - Will check if Librarian wants to update other user details or not?
            If YES:
                - Then will take the ID from the request and get the user object and return
            If NOL
                - Then will take the ID from the requested user and return requested user
        """
        if self.kwargs and "pk" in self.kwargs:
            if self.kwargs["pk"]:
                obj = get_object_or_404(User, id=self.kwargs["pk"])
            else:
                obj = self.request.user
        else:
            obj = self.request.user
        return obj

    def get(self, request, pk, *args, **kwargs):
        """
        - GET: Fetch the particular User Details API

        - Get/Fetch the particular user details from the requested User-ID
        """

        # Check if user is exist or not in request?
        if request and not request.user:
            message = (
                "User not exist in request, Please try once again with latest token!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if profile is exist or not?
        if not hasattr(request.user, "profile"):
            message = "User Profile not exist, Please contact Administrator!!!"
            return Response(get_formatted_response(200, message, {}))

        # Here member not allow to check other user detials so check role/permission
        # Check if currently logged-in user is member or librarian
        # If member then raise the error message
        if request.user.profile.is_member and not request.user.profile.is_librarian:
            message = "As You are Logged-in as Member User, you are not authorized user to access details of Librarian User Account!!!"
            return Response(get_formatted_response(200, message, {}))

        # If all the above conditions satisfied then check requested user ID is exist or not?
        # Get the user object
        try:
            user_detail_obj = self.get_object()
        except Exception as e:
            message = (
                "Requested user is not exist in system, Please try after sometime!!!"
            )
            return Response(get_formatted_response(200, message, {}))

        # Check if requested user is active or not?
        if not user_detail_obj.is_active:
            message = "The user which you trying to get Details his account is not activated, Please activate account or contact your administrator!!!"
            return Response(get_formatted_response(400, message, {}))

        # Get the serialize details of requested user
        serializer = self.serializer_class(user_detail_obj)
        # Check if details found then returns with data
        if serializer and self.kwargs["pk"]:
            message = "Fetch details successfully!!!"
            return Response(get_formatted_response(200, message, serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    POST: Logout User API

    :return:
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        """
        - POST: Logout User API

        - Logout the currently logged-in user
        - Clear the token/session
        """
        # Clear the jwt-token value from the profile
        request.user.profile.jwt_token = ""
        request.user.profile.save()
        request.user.save()

        # Logout the current request using default django logout method
        auth_logout(request)
        return Response(get_formatted_response(200, "User logged out successfully."))
