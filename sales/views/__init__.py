from .quote_views import (
    QuoteListView,
    QuoteDetailView,
    QuoteCreateView,
    QuoteUpdateView,
    QuoteDeleteView,
    QuoteConvertToOrderView,
)
from .order_views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrderConvertToSaleView,
)
from .sale_views import (
    SaleCreateView,
    SaleDeleteView,
    SaleDetailView,
    SaleListView,
    SaleUpdateView,
)

__all__ = [
    'QuoteListView',
    'QuoteDetailView',
    'QuoteCreateView',
    'QuoteUpdateView',
    'QuoteDeleteView',
    'QuoteConvertToOrderView',
    'OrderListView',
    'OrderDetailView',
    'OrderCreateView',
    'OrderUpdateView',
    'OrderDeleteView',
    'OrderConvertToSaleView',
    'SaleListView',
    'SaleDetailView',
    'SaleCreateView',
    'SaleUpdateView',
    'SaleDeleteView',
]
