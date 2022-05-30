import os

import graphene

from MyPortfolioDjango_Postgres.graphQL import graph_ql_user_authenticated
from MyPortfolioDjango_Postgres.graphQL_Types import AdminPanelType
from blog.graphQL_Types import BlogPostType
from blog.models import BlogPost, AdminPanel
from users.authentication import JWT_Authenticate
from users.graphQL_Types import UserType
from users.models import User


class Query(graphene.ObjectType):
    blog_post_for_guest = graphene.List(BlogPostType)
    adminPanel = graphene.Field(AdminPanelType)
    all_users_info = graphene.List(UserType)
    user_info = graphene.Field(UserType)

    def resolve_blog_post_for_guest(self, info, **kwargs):
        res = BlogPost.objects.filter(post_status="publish")
        return res

    @graph_ql_user_authenticated
    def resolve_adminPanel(self, info, **kwargs):
        if AdminPanel.objects.first() is None:
            AdminPanel.objects.create()
        res = AdminPanel.objects.first()
        return res

    @graph_ql_user_authenticated
    def resolve_user_info(self, info, **kwargs):
        return User.objects.get(pk=info.context.user.pk)

    def resolve_all_users_info(self, info, **kwargs):
        if not info.context.headers["Authorization"]:
            return None
        decoded = JWT_Authenticate(info.context.headers["Authorization"])
        if not decoded["is_admin"]:
            return None
        result = User.objects.all()
        return result


schema = graphene.Schema(query=Query)