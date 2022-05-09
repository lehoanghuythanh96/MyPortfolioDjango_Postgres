from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'full_name': {'required': True}
        }
