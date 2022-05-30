from django.conf.urls import url

from users.authentication import CookieTokenRefreshView, CustomTokenVerifyView
from users.views import authenticate_user, VerifyGoogleTokenId, UpdateCryptoWalletAddress

urlpatterns = [
    url(r'^token/refresh/$', CookieTokenRefreshView.as_view(), name='token_refresh'),
    url(r'^userlogin/$', authenticate_user),
    url(r'^token/verify/$', CustomTokenVerifyView.as_view(), name='token_verify'),
    url(r'^google/tokenid/verify/$', VerifyGoogleTokenId.as_view(), name='gg_tokenId_verify'),
    url(r'^user/update_wallet_address/$', UpdateCryptoWalletAddress.as_view(), name='update_wallet_address'),
]