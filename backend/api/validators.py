from django.forms import ValidationError
from recipes.models import Tag


def ingredients_validator(ingredients):
    if not ingredients:
        raise ValidationError('Отсутствуют ингредиенты.')
    for ingredient in ingredients:
        if int(ingredient['amount']) < 1:
            raise ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )


def tags_validator(tags):
    tags_count = Tag.objects.count()
    if not tags or len(tags) > tags_count:
        raise ValidationError(
            f'Количество тегов должно быть от 1 до {tags_count}.'
        )
