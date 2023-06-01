from django.conf import settings
from django.shortcuts import render
from recipes.models import User
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями"""
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
