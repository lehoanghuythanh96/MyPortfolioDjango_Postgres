from graphene_django import DjangoObjectType

from users.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"