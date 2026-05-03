from .test_forms import SaleFormTest, SaleItemFormTest
from .test_models import SaleItemModelTest, SaleModelTest
from .test_quotes import QuoteModelTest, QuoteServiceTest
from .test_orders import OrderModelTest, OrderServiceTest
from .test_services import SaleServiceTest
from .test_views import SaleCreateViewTest, SaleDetailAndDeleteViewTest, SaleListViewTest

__all__ = [
    'QuoteModelTest',
    'QuoteServiceTest',
    'OrderModelTest',
    'OrderServiceTest',
    'SaleModelTest',
    'SaleItemModelTest',
    'SaleServiceTest',
    'SaleFormTest',
    'SaleItemFormTest',
    'SaleListViewTest',
    'SaleCreateViewTest',
    'SaleDetailAndDeleteViewTest',
]

