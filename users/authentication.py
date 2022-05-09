from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from MyPortfolioDjango_Postgres import settings


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None
    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        oldToken = RefreshToken(attrs['refresh'])
        if settings.SIMPLE_JWT["CUSTOM_BLACKLIST_AFTER_ROTATION"] is True:
            RefreshToken.check_blacklist(oldToken)
        if attrs['refresh']:
            result = super().validate(attrs)
            if result and settings.SIMPLE_JWT["CUSTOM_BLACKLIST_AFTER_ROTATION"] is True:
                oldToken.blacklist()
            return result
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        newKey = serializer.validated_data["access"]
        newRefresh = serializer.validated_data["refresh"]

        response = Response()
        response.set_cookie(
            key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
            value=str(newRefresh),
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_MAXAGE'],
            secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH']
        )

        response.data = {
            "message": "Refresh token successfully",
            "access_token": newKey
        }
        response.status_code = status.HTTP_200_OK
        return response