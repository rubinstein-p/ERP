# Guía de Desarrollo: Crear Nuevos Módulos en el ERP

Fecha: 2026-05-02

## Introducción

Esta guía proporciona un paso a paso para crear nuevos módulos de negocio en el ERP Django siguiendo la arquitectura modular implementada en `core`. La arquitectura se basa en **separación de responsabilidades** entre modelos, servicios, formularios, vistas y tests.

Al final de esta guía, serás capaz de crear un módulo completo funcional (como `sales`, `purchases`, `inventory`, etc.) que se integre con el ERP.

---

## Requisitos Previos

- Python 3.12+
- Django 6.0.3+
- Familiaridad con Django (modelos, vistas basadas en clases, formularios)
- Entorno virtual activado
- Base de datos configurada

---

## Caso Práctico: Módulo Sales (Ventas)

Usaremos el módulo `sales` como ejemplo a lo largo de esta guía. El módulo tendrá:

- Modelo `Sale` (venta con header/detail)
- Servicios de negocio
- Formularios con validaciones
- Vistas CRUD
- Tests unitarios
- Templates HTML

---

## Paso 1: Estructura de Carpetas

El módulo ya existe como scaffold. Verifica que tenga esta estructura:

```
sales/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── forms/
│   └── __init__.py
├── migrations/
│   └── __init__.py
├── models/
│   └── __init__.py
├── services/
│   └── __init__.py
├── tests/
│   └── __init__.py
└── views/
    └── __init__.py
```

Si falta algo, créalo:

```bash
mkdir -p sales/forms sales/models sales/services sales/views sales/tests
touch sales/forms/__init__.py sales/models/__init__.py sales/services/__init__.py sales/views/__init__.py sales/tests/__init__.py
```

Crea la carpeta de templates:

```bash
mkdir -p sales/templates/sales
```

---

## Paso 2: Registrar la App en Settings

Abre `erp/settings.py` y verifica que `sales` esté en `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'masters',
    'purchases',
    'sales',        # ← Ya está registrada
    'inventory',
    'accounting',
    'reports',
]
```

---

## Paso 3: Definir Modelos

Los modelos deben **heredar de `BaseModel`** para obtener campos de auditoría automáticos.

Abre o crea `sales/models/sale.py`:

```python
from django.db import models
from core.models import BaseModel, User
from django.core.exceptions import ValidationError

class Sale(BaseModel):
    """
    Modelo de venta en el ERP.
    Representa una transacción de venta completa.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('partial', 'Parcial'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
    )
    
    SALE_STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    )
    
    # Datos de la venta
    sale_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Número de venta único"
    )
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Fechas
    sale_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Estados
    sale_status = models.CharField(
        max_length=20,
        choices=SALE_STATUS_CHOICES,
        default='draft'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Usuario responsable
    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales_created'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['sale_status']),
            models.Index(fields=['customer_email']),
        ]
    
    def __str__(self):
        return f"Venta {self.sale_number} - {self.customer_name}"
    
    def clean(self):
        """Validaciones a nivel de modelo."""
        if self.delivery_date and self.delivery_date < self.sale_date:
            raise ValidationError({
                'delivery_date': 'La fecha de entrega no puede ser anterior a la fecha de venta.'
            })
    
    def calculate_totals(self):
        """Recalcula subtotal, impuestos y total."""
        self.subtotal = sum(
            item.quantity * item.unit_price 
            for item in self.items.all()
        )
        self.tax = self.subtotal * 0.21  # 21% IVA
        self.total = self.subtotal + self.tax
        self.save()


class SaleItem(BaseModel):
    """Items (líneas) de una venta."""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Item de venta'
        verbose_name_plural = 'Items de venta'
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def get_total(self):
        return self.quantity * self.unit_price
```

Actualiza `sales/models/__init__.py`:

```python
from .sale import Sale, SaleItem

__all__ = ['Sale', 'SaleItem']
```

---

## Paso 4: Crear Servicios de Negocio

Los servicios **encapsulan la lógica de negocio**. Abre o crea `sales/services/sale_service.py`:

```python
from django.db import transaction
from django.core.exceptions import ValidationError
from sales.models import Sale, SaleItem
from core.services import audit_service

class SaleService:
    """Servicio de operaciones de ventas."""
    
    @staticmethod
    def create_sale(customer_name, customer_email, seller, items_data=None):
        """
        Crea una nueva venta con ítems.
        
        Args:
            customer_name: Nombre del cliente
            customer_email: Email del cliente
            seller: Usuario que registra la venta
            items_data: Lista de dicts con {product_name, quantity, unit_price}
        
        Returns:
            Sale instance
        
        Raises:
            ValidationError: Si hay datos inválidos
        """
        if not customer_name or len(customer_name.strip()) == 0:
            raise ValidationError("El nombre del cliente es requerido.")
        
        if not seller.is_staff:
            raise ValidationError("Solo usuarios staff pueden crear ventas.")
        
        try:
            with transaction.atomic():
                # Generar número de venta único
                last_sale = Sale.objects.filter(
                    is_active=True
                ).order_by('id').last()
                sale_number = f"SALE-{(last_sale.id or 0) + 1:05d}"
                
                # Crear venta
                sale = Sale.objects.create(
                    sale_number=sale_number,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    seller=seller,
                )
                
                # Crear ítems
                if items_data:
                    for item_data in items_data:
                        SaleItem.objects.create(
                            sale=sale,
                            product_name=item_data['product_name'],
                            quantity=item_data['quantity'],
                            unit_price=item_data['unit_price'],
                        )
                
                # Recalcular totales
                sale.calculate_totals()
                
                # Auditoría
                audit_service.log_action(
                    action='CREATE',
                    model_name='Sale',
                    object_id=sale.id,
                    user=seller,
                    changes={'sale_number': sale.sale_number}
                )
                
                return sale
        
        except Exception as e:
            audit_service.log_action(
                action='CREATE_FAILED',
                model_name='Sale',
                object_id=None,
                user=seller,
                changes={'error': str(e)}
            )
            raise
    
    @staticmethod
    def update_sale_status(sale, new_status, user):
        """Actualiza el estado de una venta con auditoría."""
        old_status = sale.sale_status
        sale.sale_status = new_status
        sale.save()
        
        audit_service.log_action(
            action='UPDATE',
            model_name='Sale',
            object_id=sale.id,
            user=user,
            changes={
                'sale_status': f"{old_status} → {new_status}"
            }
        )
    
    @staticmethod
    def get_sales_by_status(status):
        """Obtiene todas las ventas de un estado."""
        return Sale.objects.filter(
            sale_status=status,
            is_active=True
        ).order_by('-created_at')
    
    @staticmethod
    def get_sales_by_customer(customer_email):
        """Obtiene ventas de un cliente."""
        return Sale.objects.filter(
            customer_email=customer_email,
            is_active=True
        ).order_by('-sale_date')
```

Actualiza `sales/services/__init__.py`:

```python
from .sale_service import SaleService

__all__ = ['SaleService']
```

---

## Paso 5: Crear Formularios con Validaciones

Abre o crea `sales/forms/sale_form.py`:

```python
from django import forms
from django.core.exceptions import ValidationError
from sales.models import Sale, SaleItem

class SaleForm(forms.ModelForm):
    """Formulario para crear/editar ventas."""
    
    class Meta:
        model = Sale
        fields = ['customer_name', 'customer_email', 'customer_phone', 'delivery_date', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+54 9 123 456789'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def clean_customer_name(self):
        """Valida que el nombre no esté vacío."""
        customer_name = self.cleaned_data.get('customer_name', '').strip()
        if not customer_name:
            raise ValidationError("El nombre del cliente es requerido.")
        return customer_name


class SaleItemForm(forms.ModelForm):
    """Formulario para ítems de venta (inline)."""
    
    class Meta:
        model = SaleItem
        fields = ['product_name', 'quantity', 'unit_price']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'type': 'number'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'type': 'number'
            }),
        }
    
    def clean(self):
        """Valida que cantidad y precio sean positivos."""
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        if unit_price and unit_price < 0:
            raise ValidationError("El precio no puede ser negativo.")
        
        return cleaned_data
```

Actualiza `sales/forms/__init__.py`:

```python
from .sale_form import SaleForm, SaleItemForm

__all__ = ['SaleForm', 'SaleItemForm']
```

---

## Paso 6: Crear Vistas Basadas en Clases

Abre o crea `sales/views/sale_views.py`:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator

from core.views.mixins import StaffRequiredMixin, PermissionAuditRequiredMixin
from sales.models import Sale
from sales.services import SaleService
from sales.forms import SaleForm

class SaleListView(LoginRequiredMixin, ListView):
    """Lista de ventas con búsqueda y filtrado."""
    
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 25
    
    def get_queryset(self):
        """Filtra ventas según criterios."""
        queryset = Sale.objects.filter(is_active=True).order_by('-sale_date')
        
        # Búsqueda por número o cliente
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                models.Q(sale_number__icontains=search) |
                models.Q(customer_name__icontains=search) |
                models.Q(customer_email__icontains=search)
            )
        
        # Filtro por estado
        status = self.request.GET.get('status', '').strip()
        if status and status != 'all':
            queryset = queryset.filter(sale_status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'all')
        context['statuses'] = Sale.SALE_STATUS_CHOICES
        return context


class SaleDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una venta específica."""
    
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.filter(is_active=True)
        return context


class SaleCreateView(StaffRequiredMixin, CreateView):
    """Crear nueva venta."""
    
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')
    
    def form_valid(self, form):
        """Procesa el formulario válido."""
        try:
            form.instance.seller = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Venta {form.instance.sale_number} creada exitosamente.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error al crear venta: {str(e)}')
            return self.form_invalid(form)


class SaleUpdateView(StaffRequiredMixin, UpdateView):
    """Editar venta existente."""
    
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('sales:sale_list')
    
    def form_valid(self, form):
        """Registra cambios en auditoría."""
        old_data = Sale.objects.get(pk=self.object.pk).__dict__.copy()
        response = super().form_valid(form)
        messages.success(self.request, f'Venta {form.instance.sale_number} actualizada.')
        return response


class SaleDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar (soft delete) una venta."""
    
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('sales:sale_list')
    
    def delete(self, request, *args, **kwargs):
        """Soft delete: marca como inactiva."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(request, f'Venta {self.object.sale_number} eliminada.')
        return redirect(self.success_url)
```

Actualiza `sales/views/__init__.py`:

```python
from .sale_views import SaleListView, SaleDetailView, SaleCreateView, SaleUpdateView, SaleDeleteView

__all__ = [
    'SaleListView',
    'SaleDetailView',
    'SaleCreateView',
    'SaleUpdateView',
    'SaleDeleteView',
]
```

---

## Paso 7: Configurar URLs

Crea o edita `sales/urls.py`:

```python
from django.urls import path
from sales.views import (
    SaleListView,
    SaleDetailView,
    SaleCreateView,
    SaleUpdateView,
    SaleDeleteView,
)

app_name = 'sales'

urlpatterns = [
    path('', SaleListView.as_view(), name='sale_list'),
    path('create/', SaleCreateView.as_view(), name='sale_create'),
    path('<int:id>/', SaleDetailView.as_view(), name='sale_detail'),
    path('<int:id>/edit/', SaleUpdateView.as_view(), name='sale_edit'),
    path('<int:id>/delete/', SaleDeleteView.as_view(), name='sale_delete'),
]
```

Registra las URLs en `erp/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('core.urls')),
    path('sales/', include('sales.urls')),  # ← Agregar esta línea
    path('purchases/', include('purchases.urls')),  # (agregar cuando exista)
]
```

---

## Paso 8: Crear Templates

Crea `sales/templates/sales/sale_list.html`:

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Ventas{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="row mb-4">
        <div class="col-md-6">
            <h1>Ventas</h1>
        </div>
        <div class="col-md-6 text-end">
            <a href="{% url 'sales:sale_create' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Nueva Venta
            </a>
        </div>
    </div>

    <!-- Filtros -->
    <div class="card mb-4">
        <div class="card-body">
            <form method="get" class="row g-3">
                <div class="col-md-6">
                    <input type="text" name="search" class="form-control" 
                           placeholder="Buscar por número o cliente..." 
                           value="{{ search }}">
                </div>
                <div class="col-md-4">
                    <select name="status" class="form-select">
                        <option value="all">Todos los estados</option>
                        {% for value, label in statuses %}
                            <option value="{{ value }}" {% if status == value %}selected{% endif %}>
                                {{ label }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-outline-secondary w-100">
                        <i class="fas fa-search"></i> Buscar
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Tabla de ventas -->
    <div class="table-responsive">
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Número</th>
                    <th>Cliente</th>
                    <th>Email</th>
                    <th>Total</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for sale in sales %}
                <tr>
                    <td><strong>{{ sale.sale_number }}</strong></td>
                    <td>{{ sale.customer_name }}</td>
                    <td>{{ sale.customer_email }}</td>
                    <td>${{ sale.total|floatformat:2 }}</td>
                    <td>
                        <span class="badge bg-info">{{ sale.get_sale_status_display }}</span>
                    </td>
                    <td>{{ sale.sale_date|date:"d/m/Y" }}</td>
                    <td>
                        <a href="{% url 'sales:sale_detail' sale.id %}" class="btn btn-sm btn-info">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="{% url 'sales:sale_edit' sale.id %}" class="btn btn-sm btn-warning">
                            <i class="fas fa-edit"></i>
                        </a>
                        <a href="{% url 'sales:sale_delete' sale.id %}" class="btn btn-sm btn-danger">
                            <i class="fas fa-trash"></i>
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="text-center text-muted">No hay ventas registradas.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Paginación -->
    {% if is_paginated %}
    <nav aria-label="Page navigation" class="mt-4">
        <ul class="pagination">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page=1">Primera</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Anterior</a>
            </li>
            {% endif %}

            {% for num in page_obj.paginator.page_range %}
            <li class="page-item {% if page_obj.number == num %}active{% endif %}">
                <a class="page-link" href="?page={{ num }}">{{ num }}</a>
            </li>
            {% endfor %}

            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}">Siguiente</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">Última</a>
            </li>
            {% endif %}
        </ul>
    </nav>
    {% endif %}
</div>
{% endblock %}
```

---

## Paso 9: Crear Migraciones

```bash
python manage.py makemigrations sales
python manage.py migrate sales
```

Verifica que no haya errores:

```bash
python manage.py check
```

---

## Paso 10: Crear Tests Unitarios

Crea `sales/tests/test_models.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from sales.models import Sale, SaleItem

User = get_user_model()

class SaleModelTest(TestCase):
    """Tests para el modelo Sale."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_create_sale(self):
        """Test crear una venta."""
        sale = Sale.objects.create(
            sale_number='SALE-00001',
            customer_name='Cliente Test',
            customer_email='cliente@test.com',
            seller=self.user,
        )
        
        self.assertEqual(sale.customer_name, 'Cliente Test')
        self.assertEqual(sale.sale_status, 'draft')
        self.assertTrue(sale.is_active)
    
    def test_sale_string_representation(self):
        """Test la representación en string de venta."""
        sale = Sale.objects.create(
            sale_number='SALE-00001',
            customer_name='Cliente Test',
            seller=self.user,
        )
        
        expected = 'Venta SALE-00001 - Cliente Test'
        self.assertEqual(str(sale), expected)
    
    def test_calculate_totals(self):
        """Test cálculo de totales con IVA."""
        sale = Sale.objects.create(
            sale_number='SALE-00001',
            customer_name='Cliente Test',
            seller=self.user,
        )
        
        SaleItem.objects.create(
            sale=sale,
            product_name='Producto 1',
            quantity=10,
            unit_price=100,  # 10 x 100 = 1000
        )
        
        sale.calculate_totals()
        
        self.assertEqual(sale.subtotal, 1000)
        self.assertEqual(sale.tax, 210)  # 1000 x 0.21
        self.assertEqual(sale.total, 1210)
```

Crea `sales/tests/test_services.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from sales.models import Sale
from sales.services import SaleService

User = get_user_model()

class SaleServiceTest(TestCase):
    """Tests para el servicio SaleService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.non_staff_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123',
            is_staff=False
        )
    
    def test_create_sale_success(self):
        """Test crear venta exitosamente."""
        sale = SaleService.create_sale(
            customer_name='Cliente Test',
            customer_email='cliente@test.com',
            seller=self.user,
            items_data=[
                {'product_name': 'Producto 1', 'quantity': 5, 'unit_price': 100},
            ]
        )
        
        self.assertIsNotNone(sale.id)
        self.assertEqual(sale.customer_name, 'Cliente Test')
        self.assertEqual(sale.items.count(), 1)
    
    def test_create_sale_non_staff_fails(self):
        """Test que no-staff no puede crear ventas."""
        with self.assertRaises(ValidationError):
            SaleService.create_sale(
                customer_name='Cliente Test',
                customer_email='cliente@test.com',
                seller=self.non_staff_user,
            )
    
    def test_get_sales_by_status(self):
        """Test obtener ventas por estado."""
        # Crear venta en draft
        SaleService.create_sale(
            customer_name='Cliente Test',
            customer_email='cliente@test.com',
            seller=self.user,
        )
        
        sales = SaleService.get_sales_by_status('draft')
        self.assertEqual(sales.count(), 1)
```

Actualiza `sales/tests/__init__.py`:

```python
from .test_models import SaleModelTest
from .test_services import SaleServiceTest

__all__ = ['SaleModelTest', 'SaleServiceTest']
```

Ejecuta los tests:

```bash
python manage.py test sales
```

---

## Paso 11: Registrar en Admin (Opcional)

Abre `sales/admin.py`:

```python
from django.contrib import admin
from sales.models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ['product_name', 'quantity', 'unit_price']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'customer_name', 'total', 'sale_status', 'created_at']
    list_filter = ['sale_status', 'created_at']
    search_fields = ['sale_number', 'customer_name', 'customer_email']
    readonly_fields = ['sale_number', 'created_at', 'updated_at']
    inlines = [SaleItemInline]
    
    fieldsets = (
        ('Información de Venta', {
            'fields': ('sale_number', 'sale_date', 'seller')
        }),
        ('Datos del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Montos', {
            'fields': ('subtotal', 'tax', 'total')
        }),
        ('Estado', {
            'fields': ('sale_status', 'payment_status', 'delivery_date')
        }),
        ('Adicional', {
            'fields': ('notes', 'is_active', 'created_at', 'updated_at')
        }),
    )
```

---

## Checklist de Implementación

Antes de considerar el módulo completo, verifica:

- [ ] Carpetas de estructura creadas
- [ ] App registrada en `INSTALLED_APPS`
- [ ] Modelos definidos y heredan de `BaseModel`
- [ ] Servicios implementados (lógica de negocio)
- [ ] Formularios con validaciones
- [ ] Vistas CRUD creadas
- [ ] URLs configuradas en `urls.py` y registradas en `erp/urls.py`
- [ ] Templates HTML listos (list, detail, form, delete)
- [ ] Migraciones creadas y ejecutadas
- [ ] `python manage.py check` sin errores
- [ ] Tests unitarios creados y pasan
- [ ] Admin registrado (si aplica)
- [ ] Módulo integrado en navbar (si aplica)
- [ ] Documentación de negocio del módulo completada

---

## Resumen de Patrones

| Componente | Ubicación | Patrón |
|-----------|-----------|---------|
| **Modelos** | `models/*.py` | Heredar `BaseModel`, usar `ForeignKey` con `on_delete=models.PROTECT` |
| **Servicios** | `services/*.py` | Métodos estáticos, excepciones claras, auditoría automática |
| **Formularios** | `forms/*.py` | Heredar `ModelForm`, validaciones personalizadas en `clean()` |
| **Vistas** | `views/*.py` | Heredar CBV (`ListView`, `DetailView`, etc.), usar mixins |
| **URLs** | `urls.py` | Namespace `app_name`, `pk_url_kwarg='id'` para seguridad |
| **Templates** | `templates/app/` | Heredar `base.html`, usar Bootstrap 5, favicons Font Awesome |
| **Tests** | `tests/*.py` | Una clase por modelo/servicio, `setUp()` para fixtures |

---

## Recursos Útiles

- [Django Models Documentation](https://docs.djangoproject.com/en/6.0/topics/db/models/)
- [Django Class-Based Views](https://docs.djangoproject.com/en/6.0/topics/class-based-views/)
- [Django Forms Documentation](https://docs.djangoproject.com/en/6.0/topics/forms/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/6.0/topics/testing/)
- Referencia: Archivo `core/` en este repositorio

---

## Próximos Pasos

Después de crear un módulo exitosamente:

1. Agregar tests de integración
2. Agregar búsqueda avanzada/filtrado
3. Agregar exportación a reportes (PDF, Excel)
4. Agregar validaciones de negocio más complejas
5. Documentar endpoints en API (si aplica)
