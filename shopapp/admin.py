from io import TextIOWrapper
from csv import DictReader

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    '''
    Настраиваем отображение связанных объектов
    Указываем модель, которая будет использоваться для отображения данных
    '''
    model = Product.orders.through

class ProductInline(admin.TabularInline):
    '''
    Настраиваем отображение связанных объектов
    Указываем модель, которая будет использоваться для отображения данных
    '''
    model = Order.products.through


class ProductImagesInline(admin.StackedInline):
    '''
    Настраиваем отображение связанных объектов
    т.к. связь один ко многим достаточно просто указаь модель
    '''
    model = ProductImage


@admin.action(description='Archive products')
def mark_archived(model_admin: admin.ModelAdmin, request: HttpRequest,
                  query_set: QuerySet):
    '''Архивация продуктов - групповое действие'''
    query_set.update(archive=True)


@admin.action(description='Unarchive products')
def mark_unarchived(model_admin: admin.ModelAdmin, request: HttpRequest,
                  query_set: QuerySet):
    '''Деархивация продуктов - групповое действие'''
    query_set.update(archive=False)


# Регистрируем нашу модель - первый способ
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    '''
    Настраиваем отображение модели. Регистрация модели.
    actions - Архивация/деархивация продуктов - групповое действие
    inlines - Настраиваем отображение связанных объектов
    list_display - Перечисляем поля, которые хотим чтобы отображались
    list_display_links - Перечисляем поля, которые будут ссылками на объект
    ordering - Настраиваем сортировку по возрастанию по 'pk', в конце запятую поставить
    search_fields - Настраиваем поиск по полям, указываем именно description,
    а не descriprton_short, т.к. поиск будет происходить именно по нему
    fieldsets - Настраиваем группировку полей (что будет отображено в админе)
    '''

    change_list_template = 'shopapp/products_changelist.html'
    actions = [
        mark_archived,
        mark_unarchived,
        'export_csv',
    ]
    inlines = [
        OrderInline,
        ProductImagesInline
    ]
    # descriprton_short - функция по обрезке и отражению description
    list_display = 'pk', 'name', 'descriprton_short', 'price', 'amount', 'archive'
    list_display_links = 'pk', 'name'
    ordering = 'pk',
    search_fields = 'name', 'description', 'price'
    fieldsets = [
        (None, {
            'fields': ('name', 'description'),
        }),
        ("Selling options", {
            'fields': ('price', 'amount'),
            'classes': ('collapse', 'wide')
        }),
        ('Extra options', {
            'fields': ('archive',),
            'classes': ('collapse',),
            'description': 'Extra options. The field is for soft delete.',
        }),
        ('Images', {
            'fields': ('preview',),
        }),
    ]

    # Настрока descriprton_short для админа
    def descriprton_short(self, obj: Product) -> str:
        if len(obj.description) < 20:
            return obj.description
        return obj.description[:20] + '...'
    # Настраиваем сортировку по убыванию по 'pk', в конце запятую поставить
    # ordering = '-pk',
    # Настраиваем сортировку по возрастанию по 'name', 'pk',
    # в конце запятую можно не ставить т.к. больше 1 элемента
    # ordering = 'name', 'pk'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        '''
        Метод импортирует данные CSV файла в БД
        :param request: request
        :return: redirect
        '''
        if request.method == 'GET':
            my_form = CSVImportForm()
            context = {
                'form': my_form
            }
            return render(request, 'admin/csv_form.html', context=context)

        form = CSVImportForm(request.POST, request.FILES) # читаем форму
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html',
                          context=context, status=400)

        csv_read_file = TextIOWrapper(
            form.files['csv_file_to_save'].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_read_file) #читаем файл

        products = [
            Product(**row) for row in reader # сохраняем в БД
        ]
        Product.objects.bulk_create(products)
        self.message_user(request, 'Data imported')

        return redirect('..') # перейдет на страницу выше

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import-products-csv/',
                 self.import_csv,
                 name='import_products_csv'),
        ]
        return new_urls + urls




@admin.action(description='Set Done for order')
def set_order_done(model_admin: admin.ModelAdmin, request: HttpRequest,
                  query_set: QuerySet):
    '''Отметка заказа как выполненного'''
    query_set.update(is_done=True)


@admin.action(description='Set Undone for order')
def set_order_undone(model_admin: admin.ModelAdmin, request: HttpRequest,
                   query_set: QuerySet):
    '''Отметка заказа как НЕвыполненного'''
    query_set.update(is_done=False)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    '''Настраиваем отображение связанных объектов'''
    change_list_template = 'shopapp/orders_changelist.html'

    actions = [
        set_order_done,
        set_order_undone,
    ]
    inlines = [
        ProductInline,
    ]
    list_display = 'delivery_address', 'promocode', 'user_verbose', 'created_at', 'receipt'
    search_fields = 'delivery_address', 'user__username'
    fieldsets = [
        ("Delivery details", {
            'fields': ('user', 'delivery_address', 'products'),
            'classes': ('collapse', 'wide')
        }),
        ("Other details", {
            'fields': ('promocode', 'is_done', 'receipt'),
        })
    ]


    # Оптимизация запроса
    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    # На случай если у пользователя нет first_name - отражение атрибута связанного объекта
    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        '''
        Метод импортирует данные CSV файла в БД
        :param request: request
        :return: redirect
        '''
        if request.method == 'GET':
            my_form = CSVImportForm()
            context = {
                'form': my_form
            }
            return render(request, 'admin/csv_form.html', context=context)

        form = CSVImportForm(request.POST, request.FILES)  # читаем форму
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html',
                          context=context, status=400)

        csv_read_file = TextIOWrapper(
            form.files['csv_file_to_save'].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_read_file)  # читаем файл

        # Создаем кэш-словарь всех пользователей и продуктов {username: объект_User}
        users_dict = {user.username: user for user in User.objects.all()}
        products_dict = {product.name: product for product in Product.objects.all()}

        for row in reader:
            username_from_csv = row['user']

            # Ищем пользователя в словаре Python (работает мгновенно)
            user_obj = users_dict.get(username_from_csv)

            if user_obj:
                order = Order.objects.create(
                    delivery_address=row['delivery_address'],
                    promocode=row['promocode'],
                    user=user_obj
                )

            # 3. Обрабатываем продукты (разбиваем строку
            # 'Strawberry;Chocolate White'
            # в список)
            products_string = row.get('products', '')
            if products_string:
                # Получаем список чистых названий:
                # ['Strawberry', 'Chocolate White']
                product_names = [name.strip() for name in products_string.split(';')
                                 if name.strip()]

                # Находим соответствующие объекты моделей
                # из нашего кэш-словаря
                actual_products = [
                    products_dict.get(name)
                    for name in product_names
                    if products_dict.get(name)
                ]

                # 4. Привязываем продукты к заказу через метод .set()
                if actual_products:
                    order.products.set(actual_products)

        self.message_user(request, 'Data imported')

        return redirect('..')  # перейдет на страницу выше


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import-orders-csv/',
                 self.import_csv,
                 name='import_orders_csv'),
        ]
        return new_urls + urls














