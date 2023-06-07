from recipes.models import Ingredient, IngredientAmount

from .serializers import get_object_or_404


def ingredient_amount_set(recipe, ingredients_data):
    """Создает связи рецепта с количеством ингредиента."""
    for ingredient_data in ingredients_data:
        id = ingredient_data.get('id')
        ingredient_id = get_object_or_404(Ingredient, id=id)
        amount = ingredient_data.get('amount')
        IngredientAmount.objects.create(
            recipe=recipe, ingredient=ingredient_id, amount=amount
        )
