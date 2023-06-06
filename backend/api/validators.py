from django.forms import ValidationError

from .serializers import Tag


def ingredients_validator(ingredients):
    if not ingredients:
        raise ValidationError('Отсутствуют ингредиенты.')
    for ingredient in ingredients:
        if int(ingredient['amount']) <= 0:
            raise ValidationError('Количество должно быть положительным!')


def tags_validator(tags):
    if not tags or len(tags) > 3:
        raise ValidationError('Количество тегов должно быть от 1 до 3')
    for tag in tags:
        if tag not in Tag.objects.values_list('id', flat=True):
            raise ValidationError('Указан несуществующий тег')
