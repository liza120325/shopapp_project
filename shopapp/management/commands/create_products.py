from django.core.management import BaseCommand
from ...models import Product

# Называем именно Command - т.к. по нему будет выполняться команда
class Command(BaseCommand):
    '''
    Команда создает новый продукт в БД
    '''

    # ПЕРЕОПРЕДЕЛЯЕМ метод HANDLE
    def handle(self, *args, **options):
        self.stdout.write('Create product') # Поможет в дальнейшем тестировать была ли выполнена команда

        products = [
            {
                "name": "Grapes",
                "description": "Fresh and sweet",
                "price": 100.50,
            },
            {
                "name": "Strawberry",
                "description": "Organic, no pesticides",
                "price": 188.90,
            },
            {
                "name": "Chocolate",
                "description": "Handmade, with love",
                "price": 300.98,
            }
        ]

        for i_product in products:
            # Добавляем две звездочки перед словарем **, иначе не сработает
            product, created = Product.objects.get_or_create(**i_product)
            self.stdout.write(f'Created product {product.name}')

        self.stdout.write(self.style.SUCCESS('Product created'))