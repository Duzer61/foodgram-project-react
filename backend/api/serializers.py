from django.db.models import F
from django.forms import ValidationError

from rest_framework import serializers

from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag, User)
from users.models import Follow

from .extra_fields import Base64ImageField
from .utils import ingredient_amount_set


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed')
        read_only_fields = ['is_subscribed']
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создает нового пользователя."""
        user = User.objects.create_user(**validated_data)
        return user

    def get_is_subscribed(self, following):
        """Определяет подписан ли пользователь на данного автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=following).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class FavouriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']

    def validate_favorite(self, data, user, recipe):
        """Валидация добавления и удаления из избранного."""

        if self.context.get('request').method == 'POST':
            if Favourites.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в избранном.')
            return data

        if self.context.get('request').method == 'DELETE':
            if Favourites.objects.filter(user=user, recipe=recipe).exists():
                return data
            raise ValidationError('Этого рецепта нет в избранном.')

    def validate_shopping_cart(self, data, user, recipe):
        """Валидация добавления и удаления в список покупок."""

        if self.context.get('request').method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в списке покупок.')
            return data

        if self.context.get('request').method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return data
            raise ValidationError('Этого рецепта нет в списке покупок.')

    def validate(self, data):
        """Вызов валидирующей функции и возврат валидированных данных."""

        user = self.context.get('request').user
        recipe = self.instance

        if self.context.get('action_name') == 'favorite':
            return self.validate_favorite(data, user, recipe)

        if self.context.get('action_name') == 'shopping_cart':
            return self.validate_shopping_cart(data, user, recipe)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['pub_date']

    def get_ingredients(self, recipe):
        """Получает ингредиенты для рецепта."""
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_amount__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Определяет есть ли данный рецепт в избранном у пользователя."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favourites.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Определяет есть ли данный рецепт в списке покупок у пользователя."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class IngredeintAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента и количества в рецепт."""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения рецептов."""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredeintAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'name', 'text',
            'cooking_time', 'author', 'image'
        ]

    def validate_ingredients(self, data):
        """Валидация ингредиентов."""
        if not data:
            raise ValidationError('Отсутствуют ингредиенты.')
        used_ingredients = set()
        for ingredient in data:
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    'Убедитесь, что это значение больше либо равно 1.'
                )
            used_ingredients.add(ingredient['id'])
        if len(used_ingredients) != len(data):
            raise ValidationError('Ингредиенты повторяются.')
        return data

    def validate_tags(self, data):
        """Валидация тегов."""
        tags_count = Tag.objects.count()
        if not data or len(data) > tags_count:
            raise ValidationError(
                f'Количество тегов должно быть от 1 до {tags_count}.'
            )
        if len(data) != len(set(data)):
            raise ValidationError('Введенные теги повторяются.')
        return data

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        ingredient_amount_set(recipe, ingredients_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).delete()
        ingredient_amount_set(instance, ingredients_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance, context=self.context)
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    """Отображает авторов, на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = User
        read_only_fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def validate(self, data):
        user = self.context.get('request').user
        following = self.instance
        if self.context.get('request').method == 'POST':
            if Follow.objects.filter(user=user, following=following).exists():
                raise ValidationError('Вы уже подписаны.')
            if user == following:
                raise ValidationError('Нельзя подписываться на самого себя.')
            return data
        if self.context.get('request').method == 'DELETE':
            if Follow.objects.filter(user=user, following=following).exists():
                return data
            raise ValidationError('Такой подписки нет.')

    def get_is_subscribed(self, *args):
        """Возвращает True, т.к. в этом сериализаторе только подписки."""
        return True

    def get_recipes(self, obj):
        """Возвращает краткие рецепты автора."""
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', default=3)
        )
        recipes = obj.recipes.all()[:recipes_limit]
        serializer = FavouriteRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, following):
        """Определяет сколько рецептов создано пользователем."""
        return following.recipes.count()
