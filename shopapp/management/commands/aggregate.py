from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Sum

from ...models import Order, Product


class Command(BaseCommand):
    '''Аннотации и аггрегации'''
    def handle(self, *args, **options):
        self.stdout.write('Start demo agregate')
        result = Product.objects.filter(name__contains="strawberry").aggregate(
            Avg('price'),
            Max('price'),
            min_price=Min('price'), # будет выведено под именем min_price
            count_items=Count('id'),
        )
        print(result)


        orders = Order.objects.annotate(
            total=Sum('products__price', default=0),
            # default если не будет продуктов в заказе, иначе выводит NONE
            product_count=Count('products')
        ) # считает общую сумму по заказу, обращение через products прописано в relationship

        for i_ord in orders:
            print(
                f'Order {i_ord.id}, '
                f'total products {i_ord.product_count}, '
                f'total worth {i_ord.total}'
            )
        self.stdout.write(self.style.SUCCESS('Done'))