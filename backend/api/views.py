from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import (Favourites, Ingredient, Recipe,
                            ShoppingCart, Tag, User)

from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAuthenticatedOrReadOnly, IsSubscribeOnly
from .serializers import (FavouriteRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, UserSerializer)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями"""

    http_method_names = ['get', 'post', 'head', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Дает доступ к определенным эндпоинтам только аутентифицированным
        пользователям и разрешает метод delete только для своих подписок."""

        if self.request.method == 'DELETE':
            return [IsSubscribeOnly()]
        if self.action in ['me', 'subscriptions', 'subscribe']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Просмотр своих подписок."""

        user = self.request.user
        user_following = User.objects.filter(following__user=user)
        page = self.paginate_queryset(user_following)
        serializer = FollowSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Подписка и отписка на других пользователей."""

        user = self.request.user
        following = get_object_or_404(User, id=id)
        # in_following = Follow.objects.filter(user=user, following=following)
        if request.method == 'POST':
            serializer = FollowSerializer(
                following, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status=HTTP_201_CREATED)
            # if not in_following:
            #     if user == following:
            #         raise exceptions.ValidationError(
            #             'Нельзя подписываться на самого себя.'
            #         )
            #     Follow.objects.create(user=user, following=following)
            #     serializer = FollowSerializer(
            #         following, context={'request': request}
            #     )
            #     return Response(serializer.data, status=HTTP_201_CREATED)
            # raise exceptions.ValidationError('Вы уже подписаны.')
        if request.method == 'DELETE':
            serializer = FollowSerializer(
                following, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.filter(user=user, following=following).delete()
            return Response(status=HTTP_204_NO_CONTENT)


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
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('ingredients', 'tags').all()
    )
    permission_classes = [IsAuthorOrAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""

        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
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
        if request.method == 'DELETE':
            if not in_favourite:
                raise exceptions.ValidationError(
                    'Этого рецепта нет в избранном.'
                )
            in_favourite.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта в список покупок."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingCart.objects.filter(user=user,
                                                       recipe=recipe)
        if request.method == 'POST':
            if not in_shopping_cart:
                ShoppingCart.objects.create(user=user, recipe=recipe)
                serializer = FavouriteRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=HTTP_201_CREATED
                )
            raise exceptions.ValidationError('Рецепт уже в списке покупок.')
        if request.method == 'DELETE':
            if not in_shopping_cart:
                raise exceptions.ValidationError('Этого рецепта нет в списке.')
            in_shopping_cart.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Отдает пользователю список для покупок в виде текстового файла."""

        shopping_list_text = ShoppingCart.shopping_list_text(self, request)
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        response.write(shopping_list_text)
        return response
