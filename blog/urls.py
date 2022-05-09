from django.conf.urls import url

from blog.views import uploadPostImg

urlpatterns = [
    url(r'^post/uploadimg/$', uploadPostImg.as_view()),
]