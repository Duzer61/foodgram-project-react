from django_filters import rest_framework
from rest_framework import filters

from .views import Recipe, Tag, User


class RecipeFilter(rest_framework.FilterSet):
    """Фильтр для рецептов."""
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = rest_framework.BooleanFilter(
        method='is_favorited_method')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='is_in_shopping_cart_method')

    def is_favorited_method(self, queryset, name, value):
        """Возвращает рецепты авторов, на которых подписан пользователь
            или все рецепты в зависимости от запроса."""
        if value:
            queryset = queryset.filter(favourite__user=self.request.user)
        return queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        """Возвращает рецепты, которые внесены в список покупок
            или все рецепты в зависимости от запроса."""
        if value:
            queryset = queryset.filter(
                in_shopping_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class IngredientFilter(filters.SearchFilter):
    """Меняет старнартный парметр поиска 'search' на 'name'."""
    search_param = 'name'
