from django.core.management import BaseCommand
from django.contrib.auth.models import User

from ...models import Order, Product


class Command(BaseCommand):
    '''
    Команда обновляет инфо по заказам в БД
    '''

    # ПЕРЕОПРЕДЕЛЯЕМ метод HANDLE
    def handle(self, *args, **options):
        self.stdout.write('Load orders and projects') # Поможет в дальнейшем тестировать была ли выполнена команда
        orders = Order.objects.all()
        products = Product.objects.all()

        # Обращаемся к переменной products в нашей модели Order
        for order in orders:
            for product in products:
                order.products.add(product)
        order.save()

        self.stdout.write(self.style.SUCCESS('Order updated'))