from csv import DictReader

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

csv_files = [
    {'model': Ingredient, 'filename': 'ingredients.csv',
     'fieldnames': ['name', 'measurement_unit']},
]


class Command(BaseCommand):
    """Загружает ингредиенты из файла csv."""

    def csv_loader(self, cf):
        csv_file = 'static/data/ingredients.csv'
        with open(csv_file, encoding='utf-8', newline='') as csvfile:
            reader = DictReader(csvfile, fieldnames=cf['fieldnames'])
            print(f'Загрузка в таблицу модели {cf["model"].__name__}')

            i, err, r = 0, 0, 0

            for row in reader:
                try:
                    cf['model'].objects.update_or_create(
                        name=row['name'], defaults=row
                    )
                    r += 1
                except Exception as error:
                    print(row)
                    print(
                        f'Ошибка записи в таблицу модели '
                        f'{cf["model"].__name__}, '
                        f'{str(error)}')
                    err += 1
                i += 1
            print(
                f'Всего: {i} строк. Загружено: {r} строк. '
                f'Ошибки: {err} строк.')

    def handle(self, *args, **options):
        print("Идет загрузка данных")
        for сf in csv_files:
            self.csv_loader(сf)
        print('Загрука завершена.')
