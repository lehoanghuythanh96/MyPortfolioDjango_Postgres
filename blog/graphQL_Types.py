from graphene import Field
from graphene_django import DjangoObjectType

from blog.models import BlogPost, BlogMedia, PostReadCounter
from users.graphQL_Types import UserType
from users.models import User


class BlogMediaType(DjangoObjectType):
    class Meta:
        model = BlogMedia
        fields = "__all__"


class BlogPostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        fields = "__all__"

    post_author = Field(UserType)
    post_avatar = Field(BlogMediaType)

    def resolve_post_author(parent, info):
        return User.objects.get(email=parent.post_author)

    def resolve_post_avatar(parent, info):
        return BlogMedia.objects.get(media_parent=parent.id)
