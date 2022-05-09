from django.conf.urls import url

from users.authentication import CookieTokenRefreshView

urlpatterns = [
    url(r'^token/refresh/$', CookieTokenRefreshView.as_view(), name='token_refresh'),
]