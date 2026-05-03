from django.urls import path

from masters.views import (
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    SupplierListView,
    SupplierDetailView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

app_name = 'masters'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<pk>/edit/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    # Suppliers
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<pk>/', SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<pk>/edit/', SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/<pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<pk>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]
