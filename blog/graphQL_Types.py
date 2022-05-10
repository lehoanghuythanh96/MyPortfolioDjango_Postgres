from graphene import relay, Field
from graphene_django import DjangoObjectType

from blog.models import BlogPost
from users.graphQL_Types import UserType
from users.models import User


class BlogPostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        fields = "__all__"

    post_author = Field(UserType)

    def resolve_post_author(parent, info):
        return User.objects.get(email=parent.post_author)
