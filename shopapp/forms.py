from django import forms
from django.core import validators
from django.core.validators import RegexValidator

from .models import Product, Order


class ProductForm(forms.ModelForm):
    "Валидация формы по созданию продукта"
    class Meta:
        model = Product
        # названия полей формы = названия модели БД
        fields = ['name', 'description', 'price', 'preview']

    # Позволяет делать загрузку сразу нескольких изображений за один раз
    images =forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )


class OrderForm(forms.ModelForm):
    "Валидация формы по созданию заказа"
    class Meta:
        model = Order
        # названия полей формы = названия модели БД
        fields = 'delivery_address', 'promocode', 'user', 'products'


class CSVImportForm(forms.Form):
    csv_file_to_save = forms.FileField()
