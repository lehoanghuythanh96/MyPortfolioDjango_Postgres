import os
import sys
import uuid
from math import floor

import magic
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your models here.
from django.db.models import Manager
from django.utils import timezone
from users.models import User


class BlogPost(models.Model):
    post_title = models.CharField(max_length=255, null=False)
    post_content = models.TextField(null=False)
    post_author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post_date = models.DateTimeField(default=timezone.now)
    post_type = models.CharField(max_length=55, null=False)
    post_category = models.CharField(max_length=55, null=False)
    post_status = models.CharField(max_length=55, null=False)

    def delete(self, *args, **kwargs):
        related_medias = BlogMedia.objects.filter(media_parent=self)
        for media in related_medias:
            media.delete()
        super(BlogPost, self).delete(*args, **kwargs)
        return


def where_to_save_media(self, filename):
    return f"{self.media_category}/{filename}"


class BlogMedia(models.Model):
    media_author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False)
    media_name = models.CharField(
        max_length=80, blank=True, null=True)
    media_type = models.CharField(max_length=20, blank=True, null=True)
    media_status = models.CharField(max_length=20)
    media_parent = models.ForeignKey(BlogPost, null=True, blank=True, on_delete=models.CASCADE)
    media_date = models.DateTimeField(default=timezone.now)
    media_category = models.TextField(max_length=40, null=False)
    media_file = models.ImageField(upload_to=where_to_save_media, null=False)

    def save(self, *args, **kwargs):
        new_img = Image.open(self.media_file)
        width = 2200
        new_name = f"{uuid.uuid4()}.{new_img.format.lower()}"

        output = BytesIO()

        if new_img.size[0] > width:
            new_height = floor(width * (new_img.size[1] / new_img.size[0]))
            res_img = new_img.resize((width, new_height), Image.ANTIALIAS)
            res_img.save(output, format=new_img.format)
        else:
            new_img.save(output, format=new_img.format)

        img_mime = magic.from_buffer(output.getvalue(), mime=True)
        self.media_file = InMemoryUploadedFile(output, None, new_name, img_mime,
                                               sys.getsizeof(output), None)

        self.media_type = img_mime
        self.media_name = new_name
        super(BlogMedia, self).save(*args, **kwargs)
        return

    def delete(self, *args, **kwargs):
        path = self.media_file.path
        if os.path.isfile(path):
            os.remove(path)
        super(BlogMedia, self).delete(*args, **kwargs)
        return


class AdminPanel(models.Model):
    pass
