from django.urls import path

from sales.views import (
    QuoteListView,
    QuoteDetailView,
    QuoteCreateView,
    QuoteUpdateView,
    QuoteDeleteView,
    QuoteConvertToOrderView,
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrderConvertToSaleView,
    SaleCreateView,
    SaleDeleteView,
    SaleDetailView,
    SaleListView,
    SaleUpdateView,
)

app_name = 'sales'

urlpatterns = [
    # Presupuestos
    path('quotes/', QuoteListView.as_view(), name='quote_list'),
    path('quotes/create/', QuoteCreateView.as_view(), name='quote_create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote_detail'),
    path('quotes/<int:pk>/edit/', QuoteUpdateView.as_view(), name='quote_update'),
    path('quotes/<int:pk>/delete/', QuoteDeleteView.as_view(), name='quote_delete'),
    path('quotes/<int:pk>/convert-to-order/', QuoteConvertToOrderView.as_view(), name='quote_convert_to_order'),

    # Pedidos
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:pk>/convert-to-sale/', OrderConvertToSaleView.as_view(), name='order_convert_to_sale'),

    # Ventas
    path('', SaleListView.as_view(), name='sale_list'),
    path('create/', SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('<int:pk>/edit/', SaleUpdateView.as_view(), name='sale_update'),
    path('<int:pk>/delete/', SaleDeleteView.as_view(), name='sale_delete'),
]
