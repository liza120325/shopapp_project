import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models import CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_review_directory_path(instance: "Product", filename: string) -> str:
    return 'products/product_{pk}/preview/{file}'.format(
        pk=instance.pk,
        file=filename
    )


# Создаем модель продукта, наследуем от models.Model
class Product(models.Model):
    '''
    Модель представляет товар, который можно продавать в магазине.

    Заказы: :model:`shopapp.order`
    '''
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.PositiveSmallIntegerField(default=200)
    date_produced = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)

    preview = models.ImageField(null=True, blank=True, upload_to=product_review_directory_path)

    # Определяем отражение продукта в админке
    def __str__(self) -> str:
        return f'Product (primary_key={self.pk}, name={self.name!r})'

    def get_absolute_url(self):
        '''Метод генерирует ссылку именно для этого элемента'''
        return reverse('shopapp:product_details',
                       kwargs={'pk': self.pk})


def product_images_directory_path(instance: "ProductImage", filename: string) -> str:
    return 'products/product_{pk}/images/{file}'.format(
        pk=instance.product.pk,
        file=filename
    )


class ProductImage(models.Model):
    '''
    Модель хранит отдельное изображение продукта
    '''
    class Meta:
        verbose_name = _('ProductImage')
        verbose_name_plural = _("ProductImages")

    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.TextField(null=False, blank=True)



class Order(models.Model):
    '''
    Модель представляет заказ с продуктами для доставки.
    '''
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=False)
    promocode = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # При удалении пользователя удаляем и его заказы
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # related_name поможет получить список заказов
    products = models.ManyToManyField(Product, related_name='orders')
    is_done = models.BooleanField(default=False)

    # null=True прописываем т.к. у нас уже есть заказы, но без такого поля
    receipt = models.FileField(null=True, upload_to='orders/receipts/')
