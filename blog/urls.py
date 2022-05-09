from django.conf.urls import url

urlpatterns = [
    url(r'^post/uploadimg/$', uploadPostImg.as_view()),
]