from .models import User
from django.contrib import auth
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True, max_length=68, min_length=8)

    # redirect_url = serializers.URLField(required=False, write_only=True)

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


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    class Meta:
        fields = ['email', 'code']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200, min_length=3)
    password = serializers.CharField(write_only=True, required=True, max_length=68, min_length=8)
    username = serializers.CharField(max_length=200, read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access': user.token()['access'],
            'refresh': user.token()['refresh'],
        }

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
            'tokens': user.token()
        }


class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=100, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(_('The reset link is invalid.'), 401)

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed(_('The reset link is invalid.'), 401)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is expired or invalid.')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('Bad Token')
