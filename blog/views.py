import os
import uuid

import magic
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import BlogMedia
from blog.serializers import BlogMediaSerializer, BlogPostSerializer


def deleteMediaInArray(media_items):
    for item in media_items.iterator():
        if item.media_path is not None:
            realpath = f"{settings.MEDIA_ROOT}/{item.media_path}"
            if os.path.isfile(realpath):
                os.remove(realpath)
            item.delete()


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
        if img_category in settings.MEDIA_CATEGORIES:
            print(img_category)
        else:
            return Response(
                {"message": f"Invalid image category, must be {settings.MEDIA_CATEGORIES.keys()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        _name, _ext = os.path.splitext(upload.name)
        newName = str(uuid.uuid4()) + _ext

        postMediaFolder = f"{settings.MEDIA_ROOT}/{settings.POST_MEDIA_FOLDER}"
        if not os.path.isdir(postMediaFolder):
            os.mkdir(postMediaFolder)

        fss = FileSystemStorage()
        fss.save(f"{settings.POST_MEDIA_FOLDER}/{newName}", upload)

        media_path = f"{postMediaFolder}/{newName}"
        file_type = magic.from_file(media_path, mime=True)

        if (file_type not in ['image/jpeg', 'image/png']):
            if os.path.isfile(media_path):
                os.remove(media_path)
                return Response({"message": "This file type is not allowed!"},
                                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        newMedia = BlogMedia(
            media_name=newName,
            media_author=request.user,
            media_path=f"{settings.POST_MEDIA_FOLDER}/{newName}",
            media_type=file_type,
            media_status="trash",
            media_parent=None,
            media_category=settings.MEDIA_CATEGORIES[img_category]
        )
        BlogMedia.save(newMedia)

        serializer = self.serializer_class(newMedia)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
            imgList.append(item['media_name'])
        allTrashMedia = BlogMedia.objects.filter(media_status="trash")
        for item in allTrashMedia.iterator():
            if item.media_name in imgList:
                item.media_status = "publish"
                item.media_parent = newPost
                item.save()
                print(item.media_name)
        return Response({"message": "Post saved successfully"}, status=status.HTTP_201_CREATED)


class DeleteAllTrashMedia(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        try:
            allTrashMedia = BlogMedia.objects.filter(media_status="trash")
            deleteMediaInArray(allTrashMedia)
            return Response({"message": "All trash media successfully deleted"}, status=status.HTTP_200_OK)
        except BaseException as error:
            print(error)
            return Response({"message": "Can not execute command"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
