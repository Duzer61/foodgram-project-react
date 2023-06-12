from django_filters import rest_framework

from .views import Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name='author')
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    #is_favorited = rest_framework.BooleanFilter(field_name='is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']