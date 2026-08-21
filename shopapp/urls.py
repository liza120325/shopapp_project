from django.urls import path, include
from django.views.decorators.cache import cache_page
from .views import (ShopIndexView, ProductsListView, OrdersListView,
                    ProductsDetailsView, OrderDetailsView,
                    ProductCreateView, ProductUpdateView, OrderCreateView, OrderUpdateView,
                    ProductDeleteView, OrderDeleteView, ProductsDataExportView,
                    OrdersDataExportView)



app_name = 'shopapp'
urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),

    path('products/', cache_page(60 * 1)(ProductsListView.as_view()), name='products'),
    path('products/<int:pk>/', ProductsDetailsView.as_view(), name='product_details'),
    path('products/create/', ProductCreateView.as_view(), name='add_product'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='update_product'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='delete_product'),
    path('products-export/', ProductsDataExportView.as_view(), name='products-export'),

    path('orders/', OrdersListView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailsView.as_view(), name='order_details'),
    path('orders/create/', OrderCreateView.as_view(), name='place_order'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='update_order'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='delete_order'),
    path('orders-export/', OrdersDataExportView.as_view(), name='orders-export'),
]
