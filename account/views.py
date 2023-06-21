from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserRegisterSerializer, EmailVerificationSerializer, LoginSerializer
from .models import User
from .utils import Util
import jwt


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)

        # Creating new User
        if serializer.is_valid():
            serializer.save()

            # Get user by email and create JWT Token
            email = serializer.data['email']
            user = User.objects.get(email=email)
            token = RefreshToken.for_user(user).access_token

            # Composing a mail message
            current_site_domain = get_current_site(request).domain
            relative_link = reverse('verify-email')
            absolute_url = f"http://{current_site_domain}{relative_link}?token={token}"
            email_body = f"Здравствуйте! {user.username},\nВаш email был указан при регистрации на сайте excoin.kg \n" \
                         f"Для подтверждения регистрации в системе воспользуйтесь с ссылкой ниже: \n\n{absolute_url}\n\n" \
                         f"Если Вы получили это сообщение, но не подавали заявку на регистрацию, \nвозможно кто-то указал Ваш e-mail по ошибке. \nВ этом случае просто проигнорируйте это сообщение."
            email_data = {
                'email_body': email_body,
                'email_subject': 'Подтвердите свою регистрацию',
                'to_email': user.email
            }
            Util.send_email(email_data)

            return Response({
                'response': 'User successfully created. A message was send to the mail.'
            }, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data)


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            print(user)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Account successfully verified'}, status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Account activation Expired'}, status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
