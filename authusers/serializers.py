# -*- coding: utf-8 -*-
"""
    - Used to create custom Serializer class and if required then override the default Serializer class
"""
from __future__ import unicode_literals

# Default django import
from django.contrib.auth.models import User

# 3rd party app imports
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings

# Custom app import
from authusers.models import UserProfile

# 3rd part app, JWT authentication/secutiry settings imports for token generation
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CustomJWTSerializer(JSONWebTokenSerializer):
    """
    - Overridet the JWT default serializer while requesting the Login API
    - Override the "validate" method and check the cases with all posibilities
    """

    username_field = "username"

    def validate(self, attrs):
        """
        - Used to Validate the Login request with valid params or not?
        - Also check with user exist or not?
        - Also generate the JWT token
        """
        success = False
        password = attrs.get("password")
        user_obj = User.objects.filter(
            username__iexact=attrs.get("username").lower()
        ).first()

        if user_obj is not None:
            if user_obj.profile:
                credentials = {"username": user_obj.username, "password": password}
                if all(credentials.values()):
                    message, success, user = user_obj.profile.login_validation(
                        user_obj, password, success
                    )
                    if message:
                        raise serializers.ValidationError(message)

                    if success and user:
                        payload = jwt_payload_handler(user)
                        return {
                            "token": jwt_encode_handler(payload),
                            "user": user,
                        }
                    else:
                        raise serializers.ValidationError(message)
                else:
                    msg = "Must include username and password"
                    msg = msg.format(username_field=self.username_field)
                    raise serializers.ValidationError(msg)
            else:
                msg = "Not Authorised to access this application"
                raise serializers.ValidationError(msg)
        else:
            msg = "Account with this username does not exists"
            raise serializers.ValidationError(msg)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    - Custom User-Profile serializer class
    - Used to manage User related Profile
    """

    class Meta:
        """
        - Meta class for User-Profile
        """

        model = UserProfile
        fields = (
            "id",
            "is_librarian",
            "is_member",
            "mobile",
            "first_name",
            "last_name",
            "branch",
            "roll_no",
            "total_books_due",
        )

    def update(self, instance, validated_data):
        """
        - Override the behaviour with update method
        - Also check with requested params with updated values to profile object
        """

        if "is_librarian" not in validated_data:
            instance.is_librarian = False

        if "is_member" not in validated_data:
            instance.is_member = False

        if "first_name" in validated_data and validated_data.get("first_name"):
            instance.first_name = instance.user.first_name = (
                validated_data.get("first_name") or ""
            )

        if "last_name" in validated_data and validated_data.get("last_name"):
            instance.last_name = instance.user.last_name = (
                validated_data.get("last_name") or ""
            )

        # updating user profile data
        for attr, value in validated_data.items():
            # Here add the condition for checking roll-no & total-books-due
            # Because we generate roll-no with dynamicallyy & according to borrow book update the count of total-books-due
            if attr != "roll_no" and attr != "total_books_due":
                setattr(instance, attr, value)

        instance.save()
        instance.user.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """
    - Used to manage User related custom Searializer
    """

    class Meta:
        """
        - Meta for User
        """

        model = User
        depth = 3
        fields = ("username", "id", "password", "email")

        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """
        - Here for sending activation link via email will consider email field
        - So, at the time of new registration request will check that this email is exist or not?
        - If exist then will raise the email already exist error message
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email already exists!. Please register with Different Username or Email..."
            )
        return value

    def create(self, validated_data):
        """
        - Override the serializers
        """
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.is_active = False
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """
    - Custom User Detail Serializer
    - At the time of particular user details API I consider this class to return the details of particular requested user
    """

    class Meta:
        """
        - Meta for User
        """

        model = User
        depth = 3
        fields = ("username", "id", "email", "first_name", "last_name")
