import logging

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from masters.forms import ProductForm
from masters.models import Product


logger = logging.getLogger(__name__)


class ProductListView(StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    """Lista de productos."""

    model = Product
    template_name = 'masters/product_list.html'
    paginate_by = 25
    permission_required = 'masters.view_product'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'supplier')
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(sku__icontains=search) | queryset.filter(name__icontains=search)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset.order_by('sku')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Product.objects.values_list('category', flat=True).distinct()
        return context


class ProductDetailView(StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    """Detalle de producto."""

    model = Product
    template_name = 'masters/product_detail.html'
    permission_required = 'masters.view_product'

    def get_queryset(self):
        return Product.objects.select_related('category', 'supplier')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['inventory'] = self.object.inventory
        except Exception:
            context['inventory'] = None
        return context


class ProductCreateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, CreateView):
    """Crear producto."""

    model = Product
    form_class = ProductForm
    template_name = 'masters/product_form.html'
    permission_required = 'masters.add_product'
    success_url = reverse_lazy('masters:product-list')
    success_message = 'Producto creado exitosamente.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception('Error inesperado al crear producto')
            form.add_error(None, 'Ocurrió un error inesperado al guardar el producto. Intenta nuevamente.')
            messages.error(self.request, 'No se pudo crear el producto por un error inesperado.')
            return self.form_invalid(form)


class ProductUpdateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, UpdateView):
    """Editar producto."""

    model = Product
    form_class = ProductForm
    template_name = 'masters/product_form.html'
    permission_required = 'masters.change_product'
    success_message = 'Producto actualizado exitosamente.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception('Error inesperado al actualizar producto %s', self.object.pk)
            form.add_error(None, 'Ocurrió un error inesperado al actualizar el producto. Intenta nuevamente.')
            messages.error(self.request, 'No se pudo actualizar el producto por un error inesperado.')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('masters:product-detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    """Eliminar producto."""

    model = Product
    template_name = 'masters/product_confirm_delete.html'
    permission_required = 'masters.delete_product'
    success_url = reverse_lazy('masters:product-list')

    def post(self, request, *args, **kwargs):
        """Implementa soft delete."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=['is_active', 'updated_at'])
        return super().delete(request, *args, **kwargs)
