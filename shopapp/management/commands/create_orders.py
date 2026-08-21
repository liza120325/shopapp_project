from typing import Sequence

from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from ...models import Order, Product


class Command(BaseCommand):
    '''
    Команда создает новый заказ в БД
    '''
    @transaction.atomic
    # ПЕРЕОПРЕДЕЛЯЕМ метод HANDLE
    def handle(self, *args, **options):
        self.stdout.write('Create order with products') # Поможет в дальнейшем тестировать была ли выполнена команда

        # Берем из БД пользователей
        user_me = User.objects.get(username='Elizaveta')
        user_sloth = User.objects.get(username='Sloth')
        # defer - Не загружаем
        # only - Загружаем
        products_seq = Product.objects.defer('description',
                                             'price',
                                             'date_produced',
                                             'amount').all()
        orders = [
            {
                "delivery_address": "China",
                "promocode": "Fresh",
                "user": user_me,
            },
            {
                "delivery_address": "Bali",
                "promocode": "autumn",
                "user": user_sloth,
            },
            {
                "delivery_address": "Germany",
                "promocode": "Fresh",
                "user": user_sloth,
            }
        ]

        for i_order in orders:
            # Добавляем две звездочки перед словарем **, иначе не сработает
            order, created = Order.objects.get_or_create(**i_order)
            self.stdout.write(f'Created order for address {order.delivery_address}')
            for product in products_seq:
                order.products.add(product)
            order.save()



        self.stdout.write(self.style.SUCCESS('Order created'))