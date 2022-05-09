from django.contrib.auth import user_logged_in
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from MyPortfolioDjango_Postgres import settings
from users.models import User


def createCredentials(request, user):
    user_logged_in.send(sender=user.__class__,
                        request=request, user=user)

    refresher = RefreshToken.for_user(user)

    response = Response()
    # response.set_cookie(
    #     key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    #     value=str(refresh.access_token),
    #     max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_MAXAGE'],
    #     secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    #     samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    #     path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
    # )

    response.set_cookie(
        key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
        value=str(refresher),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_MAXAGE'],
        secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH']
    )
    response.data = {"message": "Signed in successfully", "access_token": str(refresher.access_token)}
    response.status_code = status.HTTP_200_OK
    return response


@api_view(['POST'])
@permission_classes([AllowAny, ])
@authentication_classes([])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        try:
            user = User.objects.get(email=email)
            if user:
                if user.check_password(password) is False:
                    return Response({"message": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    res = createCredentials(request, user)
                    return res

                except BaseException as error:
                    print(error)
                    return Response({"message": "User authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "Can not authenticate with the given credentials or the account has been deactivated"},status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"message": "Email or password is wrong"}, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({"message": 'Please provide a email and a password'}, status=status.HTTP_400_BAD_REQUEST)