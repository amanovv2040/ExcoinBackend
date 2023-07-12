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
            email_body = f"""
                <div id=":mm" class="ii gt" jslog="20277; u014N:xr6bB; 1:WyIjdGhyZWFkLWY6MTc2ODk2ODY4MzA0MzA2NTk3NiIsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsW11d; 4:WyIjbXNnLWY6MTc2ODk2ODY4MzA0MzA2NTk3NiIsbnVsbCxbXV0."><div id=":mn" class="a3s aiL msg-6630441826265701694"><u></u>
                    <div style="background: linear-gradient(180deg, #10185D 0%, #2E3C8F 100%);width:100%;height:70vh;font-family:roboto,'helvetica neue',helvetica,arial,sans-serif;padding:0;margin:0">
                        <div class="m_-6630441826265701694es-wrapper-color" style="width:600px;margin:0 auto;padding-bottom:20px">
                            <a href="https://excoin-react.vercel.app/" style="display:block;padding:20px" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://netex.kg&amp;source=gmail&amp;ust=1689257642751000&amp;usg=AOvVaw0Bwzhvj8OMU6GcEZinesDR">
                                <svg xmlns="http://www.w3.org/2000/svg" width="99" height="38" viewBox="0 0 99 38" fill="none" style="display:table;vertical-align:middle;margin:0 auto">
                                    <rect width="41" height="38" rx="4" fill="#5EC983"/>
                                    <rect x="5" width="36" height="38" rx="4" fill="#ACFFC9"/>
                                    <path d="M14.313 14.448V17.9915H18.911V20.148H14.313V23.7675H20.222V26H11.444V12.2155H20.222V14.448H14.313ZM35.3597 26H32.5097C32.3197 26 32.1645 25.9525 32.0442 25.8575C31.9302 25.7625 31.8383 25.6517 31.7687 25.525L28.7857 20.452C28.754 20.5217 28.7223 20.5913 28.6907 20.661C28.6653 20.7243 28.6337 20.7845 28.5957 20.8415L25.7647 25.525C25.6823 25.6453 25.5842 25.7562 25.4702 25.8575C25.3625 25.9525 25.2232 26 25.0522 26H22.3922L26.9047 18.9035L22.5632 12.2155H25.4132C25.6032 12.2155 25.7425 12.2408 25.8312 12.2915C25.9198 12.3422 25.999 12.4245 26.0687 12.5385L29.0327 17.412C29.0643 17.336 29.0992 17.26 29.1372 17.184C29.1752 17.1017 29.2195 17.0193 29.2702 16.937L31.9302 12.586C32.0062 12.4593 32.0885 12.3675 32.1772 12.3105C32.2722 12.2472 32.3862 12.2155 32.5192 12.2155H35.2457L30.8662 18.78L35.3597 26Z" fill="#2D303B"/>
                                    <path d="M56.83 22.6085C56.9883 22.6085 57.1213 22.6655 57.229 22.7795L58.3595 23.986C57.8022 24.6953 57.1087 25.2337 56.279 25.601C55.4557 25.9683 54.474 26.152 53.334 26.152C52.3017 26.152 51.3738 25.9778 50.5505 25.6295C49.7272 25.2748 49.0273 24.784 48.451 24.157C47.8747 23.53 47.4313 22.7858 47.121 21.9245C46.8107 21.0632 46.6555 20.1227 46.6555 19.103C46.6555 18.419 46.7283 17.7698 46.874 17.1555C47.026 16.5348 47.2445 15.9648 47.5295 15.4455C47.8145 14.9262 48.1565 14.4575 48.5555 14.0395C48.9608 13.6215 49.4168 13.2668 49.9235 12.9755C50.4302 12.6778 50.9812 12.453 51.5765 12.301C52.1782 12.1427 52.8178 12.0635 53.4955 12.0635C54.0022 12.0635 54.4803 12.1078 54.93 12.1965C55.386 12.2852 55.8103 12.4087 56.203 12.567C56.5957 12.7253 56.9567 12.9185 57.286 13.1465C57.6217 13.3682 57.9225 13.612 58.1885 13.878L57.229 15.189C57.172 15.2713 57.0992 15.3442 57.0105 15.4075C56.9218 15.4708 56.8015 15.5025 56.6495 15.5025C56.4975 15.5025 56.3423 15.4487 56.184 15.341C56.032 15.2333 55.842 15.113 55.614 14.98C55.3923 14.847 55.1105 14.7267 54.7685 14.619C54.4328 14.5113 54.0053 14.4575 53.486 14.4575C52.9097 14.4575 52.3808 14.562 51.8995 14.771C51.4182 14.98 51.0033 15.284 50.655 15.683C50.313 16.0757 50.047 16.5602 49.857 17.1365C49.667 17.7128 49.572 18.3683 49.572 19.103C49.572 19.844 49.6733 20.5058 49.876 21.0885C50.085 21.6648 50.3668 22.1525 50.7215 22.5515C51.0825 22.9505 51.5005 23.2545 51.9755 23.4635C52.4568 23.6662 52.9698 23.7675 53.5145 23.7675C53.8375 23.7675 54.1288 23.7517 54.3885 23.72C54.6545 23.6883 54.8983 23.6345 55.12 23.5585C55.348 23.4825 55.5602 23.3843 55.7565 23.264C55.9592 23.1437 56.1618 22.9917 56.3645 22.808C56.4342 22.751 56.507 22.7035 56.583 22.6655C56.659 22.6275 56.7413 22.6085 56.83 22.6085ZM74.5105 19.103C74.5105 20.11 74.3395 21.0442 73.9975 21.9055C73.6619 22.7668 73.1837 23.511 72.563 24.138C71.9487 24.765 71.2077 25.259 70.34 25.62C69.4724 25.9747 68.5097 26.152 67.452 26.152C66.3944 26.152 65.4317 25.9747 64.564 25.62C63.6964 25.259 62.9522 24.765 62.3315 24.138C61.7109 23.511 61.2295 22.7668 60.8875 21.9055C60.5519 21.0442 60.384 20.11 60.384 19.103C60.384 18.096 60.5519 17.165 60.8875 16.31C61.2295 15.4487 61.7109 14.7045 62.3315 14.0775C62.9522 13.4505 63.6964 12.9597 64.564 12.605C65.4317 12.244 66.3944 12.0635 67.452 12.0635C68.5097 12.0635 69.4724 12.244 70.34 12.605C71.2077 12.9597 71.9487 13.4537 72.563 14.087C73.1837 14.714 73.6619 15.4582 73.9975 16.3195C74.3395 17.1745 74.5105 18.1023 74.5105 19.103ZM71.594 19.103C71.594 18.381 71.499 17.735 71.309 17.165C71.119 16.5887 70.8435 16.101 70.4825 15.702C70.1279 15.2967 69.694 14.9895 69.181 14.7805C68.6744 14.5652 68.098 14.4575 67.452 14.4575C66.806 14.4575 66.2265 14.5652 65.7135 14.7805C65.2005 14.9895 64.7635 15.2967 64.4025 15.702C64.0479 16.101 63.7755 16.5887 63.5855 17.165C63.3955 17.735 63.3005 18.381 63.3005 19.103C63.3005 19.8313 63.3955 20.4837 63.5855 21.06C63.7755 21.63 64.0479 22.1145 64.4025 22.5135C64.7635 22.9125 65.2005 23.2197 65.7135 23.435C66.2265 23.644 66.806 23.7485 67.452 23.7485C68.098 23.7485 68.6744 23.644 69.181 23.435C69.694 23.2197 70.1279 22.9125 70.4825 22.5135C70.8435 22.1145 71.119 21.63 71.309 21.06C71.499 20.4837 71.594 19.8313 71.594 19.103ZM80.9809 26H78.1119V12.2155H80.9809V26ZM97.1924 12.2155V26H95.7199C95.4982 26 95.3114 25.9652 95.1594 25.8955C95.0074 25.8195 94.8586 25.6928 94.7129 25.5155L87.8444 16.7755C87.8634 16.9972 87.8761 17.2157 87.8824 17.431C87.8951 17.6463 87.9014 17.8458 87.9014 18.0295V26H85.3839V12.2155H86.8849C87.0052 12.2155 87.1066 12.2218 87.1889 12.2345C87.2776 12.2408 87.3567 12.263 87.4264 12.301C87.4961 12.3327 87.5626 12.377 87.6259 12.434C87.6892 12.491 87.7589 12.567 87.8349 12.662L94.7509 21.44C94.7256 21.1993 94.7066 20.9682 94.6939 20.7465C94.6812 20.5185 94.6749 20.3032 94.6749 20.1005V12.2155H97.1924Z" fill="white"/>
                                </svg>
                            </a>
                            <div style="background-color:#ffffff;padding:20px;border-radius:5px">
                                <h2 style="padding:0;margin:0;margin-bottom:15px;line-height:26px;font-size:22px;font-style:normal;font-weight:normal;color:#3f3d3d">Здравствуйте! {user.username}</h2>
                                <p style="margin:0;font-size:14px;line-height:21px;color:#3f3d3d">Ваш email был указан при регистрации на сайте <a href="http://excoin-react.vercel.app" target="_blank" data-saferedirecturl="https://www.google.com/url?q=http://netex.kg&amp;source=gmail&amp;ust=1689257642751000&amp;usg=AOvVaw0BUNn6MdMTXuGBXYRpI1ui">excoin-react.vercel.app</a></p>
                                <p style="margin:0;font-size:14px;line-height:21px;color:#3f3d3d">Для подтверждения регистрации в системе введите код ниже:</p>
                                <br>
                                <b style="display:block;background-color:#f6f6f6;border-radius:7px;border:1px solid #ddd;padding:10px 25px;margin-bottom:20px;color:#000000;font-size:14px;font-weight:normal;text-align:center">{code}</b>
                                <br>
                                <p style="margin:0;font-size:14px;line-height:21px;color:#3f3d3d">Если Вы получили это сообщение, но не подавали заявку на регистрацию, возможно кто-то указал Ваш e-mail по ошибке. В этом случае просто проигнорируйте это сообщение.</p><div class="yj6qo"></div><div class="adL">
                            </div></div><div class="adL">
                        </div></div><div class="adL">
                    </div></div><div class="adL">
                </div></div></div>
            """
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
                code = serializer.data['code']
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
            return Response({'error': serializer.errors})
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
            relative_link = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
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
