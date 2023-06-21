from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.utils.translation import gettext_lazy as _
from django.contrib import auth


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True, max_length=68, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']

    def save(self, *args, **kwargs):
        # first_name = self.validated_data['first_name']
        # last_name = self.validated_data['last_name']
        username = self.validated_data['username']
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        email = self.validated_data['email']
        user = User(
            email=email,
            username=username,
        )

        if password != password2:
            raise serializers.ValidationError({'password': _("Password doesn't match.")})
        # if not first_name:
        #     raise serializers.ValidationError({'first_name': _('User should have a first name.')})
        # if not last_name:
        #     raise serializers.ValidationError({'last_name': _('User should have a last name.')})
        user.set_password(password)
        user.save()
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200, min_length=3)
    password = serializers.CharField(write_only=True, required=True, max_length=68, min_length=8)
    username = serializers.CharField(max_length=200, read_only=True)
    tokens = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        # import pdb
        # pdb.set_trace()
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again.')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin.')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified.')

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }
