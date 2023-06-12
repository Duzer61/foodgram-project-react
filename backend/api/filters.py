from django_filters import rest_framework

from .views import Recipe, Tag, User


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = rest_framework.BooleanFilter(method='is_favorited_method')

    def is_favorited_method(self, queryset, name, value):
        if value:
            queryset = queryset.filter(favourite__user=self.request.user)
        return queryset
        

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
