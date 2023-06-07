from django.db.models import F
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as BaseUserSerializer
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag, User
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .utils import ingredient_amount_set
from .validators import ingredients_validator, tags_validator


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей"""
    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    # def update(self, instance, validated_data):
    #     if 'password' in validated_data:
    #         password = validated_data.pop('password')
    #         instance.set_password(password)
    #     return super().update(instance, validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    
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


#class IngredientAmountReadSerializer(serializers.ModelSerializer):
#    id = serializers.IntegerField(source='ingredient.id')
#    name = serializers.CharField(source='ingredient.name')
#    measurement_unit = serializers.CharField(
#        source='ingredient.measurement_unit'
#    )
#
#    class Meta:
#        model = IngredientAmount
#        fields = ['id', 'name', 'measurement_unit', 'amount']


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

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'name', 'text', 'cooking_time', 'author'
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        ingredients_validator(ingredients)
        tags_validator(tags)
        # if ingredients == []:
        #     raise ValidationError('Отсутствуют ингредиенты.')
        # for ingredient in ingredients:
        #     if int(ingredient['amount']) <= 0:
        #         raise ValidationError('Количество должно быть положительным!')
        return data

    def create(self, validated_data):
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
