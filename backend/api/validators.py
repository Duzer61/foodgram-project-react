from django.forms import ValidationError


def ingredients_validator(ingredients):
    if not ingredients:
        raise ValidationError('Отсутствуют ингредиенты.')
    for ingredient in ingredients:
        if int(ingredient['amount']) < 1:
            raise ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )


def tags_validator(tags):
    if not tags or len(tags) > 3:
        raise ValidationError('Количество тегов должно быть от 1 до 3')
