import re

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError

User = get_user_model()


def validate_color(value):
    """Проверяет цвет тега на уникальность и соответствие hex-color."""
    if (
        Tag.objects.filter(color=value.upper()).exists()
        or Tag.objects.filter(color=value.lower()).exists()
    ):
        raise ValidationError('Такой цвет уже занят другим тегом.')
    reg = re.compile(r'^#([a-f0-9]{6}|[A-F0-9]{6})$')
    if not reg.match(value):
        raise ValidationError(
            'Введите правильный 6-значный код hex-color в одном регистре.'
        )


class Ingredient(models.Model):
    """Модель ингредиентов для рецепта"""
    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов для рецепта"""
    name = models.CharField(verbose_name='Название тега',
                            max_length=200,
                            unique=True)
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=7,
        unique=True,
        validators=[validate_color]
    )
    slug = models.SlugField(verbose_name='Слаг тега',
                            max_length=200,
                            unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField(verbose_name='Название блюда', max_length=255)
    text = models.TextField(verbose_name='Текст рецепта')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        null=True,
        on_delete=models.SET_NULL,
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингридиенты для приготовления блюда',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги для рецепта',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    """Модель для привязки количества ингредиента к рецепту"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='К какому рецепту относится',
        related_name='ingredient_amount',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='К какому ингредиенту относится',
        related_name='ingredient_amount',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента в рецепте'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class Favourites(models.Model):
    """Модель для добавления рецептов в избранное"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favourite',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='favourite',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'

    def __str__(self) -> str:
        return f'{self.recipe} - {self.user}'


class ShoppingCart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='in_shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_recipe_in_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
