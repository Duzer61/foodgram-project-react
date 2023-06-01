from recipes.models import User
from rest_framework import serializers
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        model = User
        extra_kwargs = {'password': {'write_only': True}}

