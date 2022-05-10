from django.conf.urls import url

from blog.views import uploadPostImg, SaveSingleBlogPost, DeleteAllTrashMedia, deleteallblogpost

urlpatterns = [
    url(r'^post/uploadimg/$', uploadPostImg.as_view()),
    url(r'^post/savenewpost/$', SaveSingleBlogPost.as_view()),
    url(r'^media/deleteall/$', DeleteAllTrashMedia.as_view()),
    url(r'^post/deleteall/$', deleteallblogpost.as_view()),
]