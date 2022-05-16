from django.conf import settings
# Create your views here.
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import BlogMedia, BlogPost
from blog.serializers import BlogMediaSerializer, BlogPostSerializer


class uploadPostImg(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BlogMediaSerializer

    def post(self, request, *args, **kwargs):
        upload = request.FILES['upload']
        img_category = request.POST.get('imgCategory')
        if not img_category:
            return Response({
                "message": "Please include imgCategory parameter in post request"
            }, status=status.HTTP_400_BAD_REQUEST)
        if img_category not in settings.MEDIA_CATEGORIES:
            return Response(
                {"message": f"Invalid image category, must be {settings.MEDIA_CATEGORIES.keys()}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        mediaData = {
            "media_name": upload.name,
            "media_author": request.user.id,
            "media_status": "trash",
            "media_parent": None,
            "media_category": settings.MEDIA_CATEGORIES[img_category],
            "media_file": upload
        }

        newMedia = BlogMediaSerializer(data=mediaData)
        newMedia.is_valid(raise_exception=True)
        newMedia.save()

        return Response(newMedia.data, status=status.HTTP_200_OK)


class SaveSingleBlogPost(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        postInfo = request.data["postInfo"]
        postInfo["post_author"] = request.user.id
        postInfo["post_status"] = "publish"
        postInfo["post_type"] = settings.POST_TYPES["blogPost"]
        validPostInfo = BlogPostSerializer(data=postInfo)
        validPostInfo.is_valid(raise_exception=True)
        newPost = validPostInfo.save()

        post_imgs = request.data.get('post_imgs')
        imgList = []
        for item in post_imgs:
            imgList.append(item['id'])
        BlogMedia.objects.filter(id__in=imgList, media_author=request.user.id).update(media_status="publish", media_parent=newPost)
        return Response({"message": "Post saved successfully"}, status=status.HTTP_201_CREATED)


class DeleteAllTrashMedia(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        try:
            all_trash_media = BlogMedia.objects.filter(media_status="trash")
            for item in all_trash_media:
                item.delete()
            return Response({"message": "All trash media successfully deleted"}, status=status.HTTP_200_OK)
        except BaseException as error:
            print(error)
            return Response({"message": "Can not execute command"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class deleteallblogpost(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        try:
            allPosts = BlogPost.objects.all()
            for single in allPosts:
                single.delete()
        except BaseException as error:
            print(error)
            return Response({
                "message": error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "message": "Deleted succesfully"
        }, status=status.HTTP_200_OK)


class deleteblogpostby_ids(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        if isinstance(request.data, list) is False:
            return Response(
                {
                    "message": "Please send an array of post ID"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            found_posts = BlogPost.objects.filter(id__in=request.data)
            for single in found_posts.iterator():
                single.delete()
            return Response({
                "message": "ok"
            }, status=status.HTTP_200_OK)
        except BaseException as error:
            return Response({
                "message": error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
