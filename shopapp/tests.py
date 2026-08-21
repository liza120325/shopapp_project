from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices

from .models import Product, Order
from .utils import sum_numbers


class SumNumbersTestCase(TestCase):
    def test_sum_numbers(self):
        res = sum_numbers(2, 5)
        self.assertEqual(res, 7)


class CreateProductTestCase(TestCase):
    '''Класс тестирует создание продукта'''
    def setUp(self):
        # 1. Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        # Удаляем все записи продуктов с таким же наименованием как в product_name,
        # чтобы убедиться, что наш тест действиельно создает новый продукт
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()


    def test_create_product(self):
        # 2. АВТОРИЗУЕМ пользователя в тестовом клиенте
        self.client.force_login(self.user)

        response = self.client.post(reverse('shopapp:add_product'),
                         {
                             'name': self.product_name,
                             'description': 'Lined paper',
                             'price': '50',
                         },
                         HTTP_USER_AGENT='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
                                         'Gecko/20100101 Firefox/152.0',

        )
        self.assertRedirects(response, reverse('shopapp:products'))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailTestCase(TestCase):
    '''Класс тестирует получение детальной информации о продукте'''

    @classmethod
    def setUpClass(cls):
        '''Метод создает тестового пользователя и создает
        тестовый продукт для всех тестов в классе'''
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        cls.product = Product.objects.create(name='Pen',
                                              description='blue ink',
                                              price=10,
                                              created_by=cls.user)
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'
    # def setUp(self):
    #     '''Метод создает тестового пользователя и создает тестовый продукт'''
    #     self.user = User.objects.create_user(
    #         username='testuser',
    #         password='password123'
    #     )
    #     self.product = Product.objects.create(name='Pen',
    #                                           description='blue ink',
    #                                           price=10,
    #                                           created_by=self.user)

    @classmethod
    def tearDownClass(cls):
        '''Метод удаляет все данные по завершению тестов в классе'''
        cls.product.delete()
        cls.user.delete()
    # def tearDown(self):
    #     '''Метод удаляет все данные по завершению теста'''
    #     self.product.delete()
    #     self.user.delete()

    def test_product_detail(self):
        '''Тест получает детальную информацию о продукте'''
        resp = self.client.get(reverse(
            'shopapp:product_details',
            kwargs={'pk': self.product.pk}),
            HTTP_USER_AGENT=self.HTTP_USER_AGENT,)
        self.assertEqual(resp.status_code, 200)


    def test_product_detail_and_check_content(self):
        '''Тест проверяет содержимое полученных данных'''
        resp = self.client.get(reverse(
            'shopapp:product_details',
            kwargs={'pk': self.product.pk}),
            HTTP_USER_AGENT=self.HTTP_USER_AGENT,)
        self.assertContains(resp, self.product.name)


class ProductsListViewTestCase(TestCase):
    '''Класс тестирует отображение списка продуктов'''
    # джанго автоматически будет накатывать данные перед каждым тестом из этого файла
    fixtures = [
        'groups.json',  # Сначала группы
        'users.json',  # Затем пользователи (ссылаются на группы)
        'products.json',  # Затем продукты (ссылаются на пользователей)
        'orders.json',  # В конце заказы (ссылаются на пользователей и продукты)
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'


    def test_products_list(self):
        resp = self.client.get(reverse('shopapp:products'),
                               HTTP_USER_AGENT=self.HTTP_USER_AGENT)
        # for product in Product.objects.filter(archive=False).all():
        #     self.assertContains(resp, product.name)
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archive=False).all(), # получаем данные БД
            values=list(p.pk for p in resp.context['products']), # получаем данные респонса
            # как транфсормировать полученный из БД qs
            transform=lambda p: p.pk,
            ordered=False
        )
        self.assertTemplateUsed(resp, 'shopapp/products_list.html')


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        '''Метод создает тестового пользователя'''
        cls.credentials = dict(username='testuser', password='password123')
        cls.user = User.objects.create_user(**cls.credentials) # распаковываем словарь
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'

    @classmethod
    def tearDownClass(cls):
        '''Метод удаляет все данные по завершению тестов в классе'''
        cls.user.delete()


    def setUp(self):
        self.client.login(**self.credentials)


    def test_orders_list(self):
        resp = self.client.get(reverse('shopapp:orders'), HTTP_USER_AGENT=self.HTTP_USER_AGENT)
        self.assertContains(resp, 'Orders')


class ProductsExportTestCase(TestCase):
    '''Класс тестирует экспорт продуктов в БД'''
    # джанго автоматически будет накатывать данные перед каждым тестом из этого файла
    fixtures = [
        'groups.json',  # Сначала группы
        'users.json',  # Затем пользователи (ссылаются на группы)
        'products.json',  # Затем продукты (ссылаются на пользователей)
        'orders.json',  # В конце заказы (ссылаются на пользователей и продукты)
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'


    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'),
                                   HTTP_USER_AGENT=self.HTTP_USER_AGENT)
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'description': product.description
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data['all_my_products'], expected_data)


class OrderDetailTestCase(TestCase):
    '''Класс тестирует получение детальной информации о заказе'''

    @classmethod
    def setUpClass(cls):
        '''Метод создает тестового пользователя и дает ему право просматривать заказ'''
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)
        # cls.client.force_login(cls.user)
        cls.order = Order.objects.create(delivery_address='Test_address',
                                              promocode='summer2026', user=cls.user)
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'


    @classmethod
    def tearDownClass(cls):
        '''Метод удаляет все данные по завершению тестов в классе'''
        cls.user.delete()
        cls.order.delete()


    def test_order_details(self):
        '''Тест получает детальную информацию о заказе
        Проверяет, что в теле ответа есть адрес заказа;
        Проверяет, что в теле ответа есть промокод;
        Проверяет, что в контексте ответа тот же заказ, который был создан перед тестом
        (сравнение по первичному ключу).
        '''
        self.client.force_login(self.user)
        resp = self.client.get(reverse(
            'shopapp:order_details',
            kwargs={'pk': self.order.pk}),
            HTTP_USER_AGENT=self.HTTP_USER_AGENT)

        response_data = resp.context['my_order']

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.order.delivery_address)
        self.assertContains(resp, self.order.promocode)
        self.assertEqual(response_data.pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    '''Класс тестирует экспорт заказов в БД'''
    # джанго автоматически будет накатывать данные перед каждым тестом из этого файла
    fixtures = [
        'groups.json',  # Сначала группы
        'users.json',  # Затем пользователи (ссылаются на группы)
        'products.json',  # Затем продукты (ссылаются на пользователей)
        'orders.json',  # В конце заказы (ссылаются на пользователей и продукты)
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123',
            is_staff=True
        )
        cls.HTTP_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) '
        'Gecko/20100101 Firefox/152.0'


    @classmethod
    def tearDownClass(cls):
        '''Метод удаляет все данные по завершению тестов в классе'''
        cls.user.delete()


    def test_get_orders_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('shopapp:orders-export'),
                                   HTTP_USER_AGENT=self.HTTP_USER_AGENT)
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user,
                'products': order.products,
            }
            for order in orders
        ]

        orders_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(orders_data['orders'], expected_data)


