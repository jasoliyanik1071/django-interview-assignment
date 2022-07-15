# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
# from django.contrib.auth import get_user_model
# User = get_user_model()

from authusers.models import UserProfile

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CustomJWTSerializer(JSONWebTokenSerializer):
    username_field = 'username'

    def validate(self, attrs):
        success = False
        password = attrs.get("password")
        user_obj = User.objects.filter(username__iexact=attrs.get("username").lower()).first()

        if user_obj is not None:
            if user_obj.profile:
                credentials = {
                    'username': user_obj.username,
                    'password': password
                }
                if all(credentials.values()):

                    message, success, user = user_obj.profile.login_validation(user_obj, password, success)
                    if message:
                        raise serializers.ValidationError(message)
                    if success and user:
                        payload = jwt_payload_handler(user)
                        return {
                            'token': jwt_encode_handler(payload),
                            'user': user,
                        }
                    else:
                        raise serializers.ValidationError(message)

                else:
                    msg = 'Must include username and password'
                    msg = msg.format(username_field=self.username_field)
                    raise serializers.ValidationError(msg)
            else:
                msg = 'Not Authorised to access this application'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Account with this username does not exists'
            raise serializers.ValidationError(msg)


# class UserSerializer(serializers.ModelSerializer):
#     profile = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         # model = UserProfile
#         depth = 3
#         fields = ("username", "id", "first_name", "last_name", "email", "profile", "password", "jwt_token")

#         extra_kwargs = {
#             "password": {"write_only": True}
#         }

#     def  create(self, validated_data):
#         """
#             - Override the serializers
#             - Used to set password and email
#         """
#         password = validated_data.pop("password", None)
#         instance = self.Meta.model(**validated_data)

#         if password is not None:
#             instance.set_password(password)

#         # Set Username as Email
#         instance.username = instance.email
#         instance.save()
#         return instance


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields =(
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
        # updating user data

        if "is_librarian" not in validated_data:
            instance.is_librarian = False

        if "is_member" not in validated_data:
            instance.is_member = False

        if "first_name" in validated_data and validated_data.get("first_name"):
            instance.first_name = instance.user.first_name = validated_data.get("first_name") or ""

        if "last_name" in validated_data and validated_data.get("last_name"):
            instance.last_name = instance.user.last_name = validated_data.get("last_name") or ""

        # updating user profile data
        for attr, value in validated_data.items():
            if attr != "roll_no" and attr != "total_books_due":
                setattr(instance, attr, value)

        instance.save()
        instance.user.save()

        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        depth = 3
        # fields = ("id", "username", "password", "email")
        fields = ("username", "id", "password", "email")

        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
           raise serializers.ValidationError("This email already exists!. Please register with Different Username and Email...")
        return value

    def create(self, validated_data):
        """
            - Override the serializers
            - Used to set password and email
        """
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.is_active = False
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        depth = 3
        fields = ("username", "id", "email", "first_name", "last_name")
