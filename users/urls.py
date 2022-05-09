from django.conf.urls import url

from users.authentication import CookieTokenRefreshView, CustomTokenVerifyView
from users.views import authenticate_user

urlpatterns = [
    url(r'^token/refresh/$', CookieTokenRefreshView.as_view(), name='token_refresh'),
    url(r'^userlogin/$', authenticate_user),
    url(r'^token/verify/$', CustomTokenVerifyView.as_view(), name='token_verify'),
]