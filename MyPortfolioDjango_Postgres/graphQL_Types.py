# Schemas
import graphene
from graphene_django import DjangoObjectType

from blog.graphQL_Types import BlogPostType
from blog.models import AdminPanel, BlogPost


class AdminPanelType(DjangoObjectType):

    class Meta:
        model = AdminPanel
        fields = "__all__"

    all_blog_posts = graphene.List(BlogPostType)

    def resolve_all_blog_posts(parent, info):
        return BlogPost.objects.all()