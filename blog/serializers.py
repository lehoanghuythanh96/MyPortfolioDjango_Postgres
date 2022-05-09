from rest_framework import serializers

from blog.models import BlogPost, BlogMedia


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'


class BlogMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogMedia
        fields = '__all__'