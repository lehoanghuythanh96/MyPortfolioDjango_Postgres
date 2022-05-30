from graphene import Field, List
from graphene_django import DjangoObjectType

from blog.models import PostReadCounter
from users.models import User, CryptoWallet


class UserPostReadCounterType(DjangoObjectType):
    class Meta:
        model = PostReadCounter
        fields = "__all__"


class UserCryptoWalletType(DjangoObjectType):
    class Meta:
        model = CryptoWallet
        fields = "__all__"


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"

    post_read = Field(UserPostReadCounterType)
    crypto_wallet = Field(UserCryptoWalletType)

    def resolve_post_read(parent, info):
        result = PostReadCounter.objects.filter(user=parent.pk)
        if len(result) == 0:
            this_user = User.objects.get(pk=parent.pk)
            PostReadCounter.save(PostReadCounter(user=this_user, posts=[]))
        return PostReadCounter.objects.get(user=parent.pk)

    def resolve_crypto_wallet(parent, info):
        result = CryptoWallet.objects.filter(user=parent.pk)
        if len(result) == 0:
            this_user = User.objects.get(pk=parent.pk)
            CryptoWallet.save(CryptoWallet(user=this_user))
        return CryptoWallet.objects.get(user=parent.pk)
