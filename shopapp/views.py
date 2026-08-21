'''
В этом модуле лежат различные наборы представлений.

Разные view интернет магазина: по товарам, по заказам.
'''

import logging
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from django.core.cache import cache


from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm
from .serializers import ProductSerializer, OrderSerializer


log = logging.getLogger(__name__)

class ShopIndexView(View):
    '''Класс по отражению стартовой страницы'''
    def get(self, request: HttpRequest) -> HttpResponse:
    # Метод полностью заменит функцию shop_index
        pages = [
            {'name': 'Каталог продуктов', 'url_name': 'shopapp:products'},
            {'name': 'Список заказов', 'url_name': 'shopapp:orders'},
            {'name': 'Создание продукта', 'url_name': 'shopapp:add_product'},
            {'name': 'Создание заказа', 'url_name': 'shopapp:place_order'},
        ]
        # Передаем этот список в контекст шаблона
        return render(request, 'shopapp/shop-index.html',
                      {'pages': pages})


class ProductsListView(ListView):
    '''Класс по отражению продуктов в БД'''
    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.filter(archive=False)
    print(queryset)
    context_object_name = 'products'
    log.info('visited page products list')


class OrdersListView(ListView):
    '''Класс по отражению заказов в БД.
    Доступен только авторизованным пользователем (LoginRequiredMixin)'''
    queryset = (Order.objects.select_related('user').prefetch_related('products').all())
    template_name = 'shopapp/orders_list.html'
    model = Order
    context_object_name = 'orders'


class ProductsDetailsView(DetailView):
    '''Класс по отражению конкретного продукта'''
    template_name = 'shopapp/product_details.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'my_product'



class OrderDetailsView(DetailView):
    '''Класс по отражению конкретного заказа'''
    template_name = 'shopapp/order_detail.html'
    model = Order
    context_object_name = 'my_order'

# Дайте доступ к созданию продукта только тем, у кого есть разрешение (permission).
# class ProductCreateView(PermissionRequiredMixin, CreateView):
class ProductCreateView(CreateView):
    '''Класс по созданию нового продукта'''
    # permission_required = 'shopapp.add_product'
    model = Product
    # form_class = ProductForm - то же что и строчка ниже
    fields = 'name', 'description', 'price', 'preview'
    template_name = 'shopapp/create_product.html'

    def form_valid(self, form):
        # Привязываем текущего пользователя к объекту товара
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('shopapp:products')



class ProductUpdateView(UpdateView):
    model = Product
    # fields = 'name', 'description', 'price', 'amount', 'preview'
    form_class = ProductForm # указываем какая форма используется при обновлении продукта
    template_name = 'shopapp/update_product.html'
    context_object_name = 'product'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )


    def form_valid(self, form):
        response = super().form_valid(form)
        # идем по картинкам в форме и сохраняем их всех по одной
        for new_image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=new_image,
            )
        return response


class OrderCreateView(CreateView):
    '''Класс по размещению нового заказа'''
    model = Order
    fields = 'delivery_address', 'user', 'products'
    template_name = 'shopapp/create_order.html'
    success_url = reverse_lazy('shopapp:orders')


class OrderUpdateView(UpdateView):
    '''Класс по обновлению инфо о заказе'''
    model = Order
    fields = 'delivery_address', 'user', 'products'
    template_name = 'shopapp/update_order.html'
    context_object_name = 'order'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products')

    # soft-delete на архивацию продукта
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archive = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders')


class ProductsDataExportView(View):
    '''Класс экспортирует данные по продуктам'''
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': product.price,
                'description': product.description
            }
            for product in products
        ]
        return JsonResponse({'all_my_products': products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    '''Класс экспортирует данные по заказам'''

    def test_func(self):
        """
        Метод-проверка: метод должен вернуть True, чтобы пользователя пустило.
        """
        # Проверяем, что пользователь имеет статус staff
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user,
                'products': order.products,
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})



