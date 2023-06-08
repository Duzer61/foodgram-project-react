from django.conf import settings
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favourites, Ingredient, Recipe, Tag, User
from rest_framework import (exceptions, filters, permissions, serializers,
                            viewsets)
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)

from .serializers import (FavouriteRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, UserSerializer)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями"""
    http_method_names = ['get', 'post', 'head']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        """Дает доступ к эндпоинту /me/ только
            аутентифицированным пользователям"""
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    @permission_classes([IsAuthenticated])
    def subscriptions(self):
        """Просмотр своих подписок."""
        user = self.request.user
        following = user.follower.all()
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('ingredients', 'tags').all()
    )

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'])
    @permission_classes([IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта в избанное."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_favourite = Favourites.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if not in_favourite:
                Favourites.objects.create(user=user, recipe=recipe)
                serializer = FavouriteRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=HTTP_201_CREATED
                )
            raise exceptions.ValidationError('Рецепт уже в избранном.')
        if not in_favourite:
            raise exceptions.ValidationError('Этого рецепта нет в избранном.')
        in_favourite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

