from django.core.management import BaseCommand
from django.contrib.auth.models import User

from ...models import Order, Product


class Command(BaseCommand):
    '''
    Команда выгружает только поля 'pk', 'name'
    '''
    def handle(self, *args, **options):
        self.stdout.write('Start demo select fields')
        # product_values = Product.objects.values('pk', 'name') # выгружает словарем
        # for p_val in product_values:
        #     print(p_val)

        # users_info = User.objects.values_list('username') # выгружает кортежем
        # for user_val in users_info:
        #     print(user_val)

        users_info = User.objects.values_list('username', flat=True) # выгружает списком
        for user_val in users_info:
            print(user_val)

        self.stdout.write(self.style.SUCCESS('Done'))