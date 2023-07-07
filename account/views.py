import os

from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import redirect

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .serializers import (
    UserRegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    PasswordResetEmailSerializer,
    SetNewPasswordSerializer,
    LogoutSerializer,
)
from .models import User
from .utils import Util
from .renderers import UserRenderer
import jwt
from django.http import HttpResponsePermanentRedirect
from dotenv import load_dotenv
import os
from random import randint

load_dotenv()


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.getenv('APP_SCHEME'), 'http', 'https']


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    # renderer_classes = (UserRenderer,)

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        # Creating new User
        if serializer.is_valid():
            serializer.save()

            # Get user by email and create JWT Token
            email = serializer.data['email']
            user = User.objects.get(email=email)
            user.verification_code = str(randint(100_000, 999_999))
            user.save()

            # token = RefreshToken.for_user(user).access_token
            # redirect_url = request.data.get('redirect_url', '')

            # Composing a mail message
            # current_site_domain = get_current_site(request).domain
            # relative_link = reverse('verify-email')
            # absolute_url = f"http://{current_site_domain}{relative_link}?redirect_url={redirect_url}"
            code = user.verification_code
            email_body = f"Здравствуйте! {user.username},\nВаш email был указан при регистрации на сайте excoin.kg \n" \
                         f"Для подтверждения регистрации в системе введите код ниже: \n\n{code}\n\n" \
                         f"Если Вы получили это сообщение, но не подавали заявку на регистрацию, \nвозможно кто-то указал Ваш e-mail по ошибке. \nВ этом случае просто проигнорируйте это сообщение."
            email_data = {
                'email_body': email_body,
                'email_subject': 'Подтвердите свою регистрацию',
                'to_email': user.email
            }
            Util.send_email(email_data)

            return Response({
                'response': _('User successfully created. A message was send to the mail.')
            }, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data)


class VerifyEmailCode(APIView):
    try:
        def post(self, request):
            serializer = EmailVerificationSerializer(data=request.data)

            if serializer.is_valid():
                code = serializer.data['verification_code']
                email = serializer.data['email']
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    if user.verification_code != code:
                        return Response({'error': 'Введен неправильный код'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        user.is_verified = True
                        user.save()
                        return Response({'response': _('Активация прошла успешна')}, status=status.HTTP_200_OK)
                return Response({'error': 'Введена неправльная почта'}, status=status.HTTP_400_BAD_REQUEST)
            return serializer.errors
    except Exception as error:
        print(error)


# class VerifyEmail(APIView):
#     serializer_class = EmailVerificationSerializer
#
#     token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description',
#                                            type=openapi.TYPE_STRING)
#
#     @swagger_auto_schema(manual_parameters=[token_param_config])
#     def get(self, request):
#         redirect_url = request.GET.get('redirect_url')
#         token = request.GET.get('token')
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
#             user = User.objects.get(id=payload['user_id'])
#             print(user)
#             if not user.is_verified:
#                 user.is_verified = True
#                 user.save()
#                 return CustomRedirect(f'{redirect_url}?token_valid=True&verification=True')
#             return Response({'email': _('Account successfully verified')}, status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError as identifier:
#             return Response({'error': _('Account activation Expired')}, status.HTTP_400_BAD_REQUEST)
#         except jwt.exceptions.DecodeError as identifier:
#             return Response({'error': _('Invalid token')}, status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetEmail(generics.GenericAPIView):
    serializer_class = PasswordResetEmailSerializer

    def post(self, request):
        data = {'request': request, 'data': request.data}
        serializer = self.serializer_class(data=data)
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            # Get user by email and create Reset Token
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Composing a mail message
            redirect_url = request.data.get('redirect_url', '')
            current_site = get_current_site(request=request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absolute_url = f"http://{current_site}{relative_link}"
            email_body = f"Здравствуйте! {user.username},\nВы запросили восстановление пароля для Вашей учетной записи: {user.email}\n" \
                         f"Чтобы восстановить пароль воспользуйтесь ссылкой ниже: \n\n{absolute_url}?redirect_url={redirect_url}\n\n"
            data = {
                'email_body': email_body,
                'email_subject': 'Восстановление пароля',
                'to_email': user.email
            }
            Util.send_email(data)
            return Response({'success': _('We have sent you a link to reset your password')}, status=status.HTTP_200_OK)
        return Response({'error': _('Пользователь не зарегистрирован')})


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(f"{redirect_url}?token_valid=False")
                else:
                    return CustomRedirect(os.getenv(f"{os.getenv('FRONTEND_URL')}?token_valid=False"))

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    f"{redirect_url}?token_valid=True&?message=Credential Valid&?uidb64={uidb64}&?token={token}")
            else:
                return CustomRedirect(os.getenv(f"{os.getenv('FRONTEND_URL')}?token_valid=False"))

        except DjangoUnicodeDecodeError:
            return CustomRedirect(f"{redirect_url}?token_valid=False")


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': _('Password reset successfully done.')}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
