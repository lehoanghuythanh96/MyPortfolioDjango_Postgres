from django.conf.urls import url

from users.authentication import CookieTokenRefreshView, CustomTokenVerifyView
from users.views import authenticate_user, VerifyGoogleTokenId

urlpatterns = [
    url(r'^token/refresh/$', CookieTokenRefreshView.as_view(), name='token_refresh'),
    url(r'^userlogin/$', authenticate_user),
    url(r'^token/verify/$', CustomTokenVerifyView.as_view(), name='token_verify'),
    url(r'^google/tokenid/verify/$', VerifyGoogleTokenId.as_view(), name='gg_tokenId_verify'),
]