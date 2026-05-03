import logging

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from masters.forms import SupplierForm
from masters.models import Supplier


logger = logging.getLogger(__name__)


class SupplierListView(StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    """Lista de proveedores."""

    model = Supplier
    template_name = 'masters/supplier_list.html'
    paginate_by = 25
    permission_required = 'masters.view_supplier'

    def get_queryset(self):
        queryset = Supplier.objects.filter(is_active=True)
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(email__icontains=search)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SupplierDetailView(StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    """Detalle de proveedor."""

    model = Supplier
    template_name = 'masters/supplier_detail.html'
    permission_required = 'masters.view_supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_active=True)
        return context


class SupplierCreateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, CreateView):
    """Crear proveedor."""

    model = Supplier
    form_class = SupplierForm
    template_name = 'masters/supplier_form.html'
    permission_required = 'masters.add_supplier'
    success_url = reverse_lazy('masters:supplier-list')
    success_message = 'Proveedor creado exitosamente.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception('Error inesperado al crear proveedor')
            form.add_error(None, 'Ocurrió un error inesperado al guardar el proveedor. Intenta nuevamente.')
            messages.error(self.request, 'No se pudo crear el proveedor por un error inesperado.')
            return self.form_invalid(form)


class SupplierUpdateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, UpdateView):
    """Editar proveedor."""

    model = Supplier
    form_class = SupplierForm
    template_name = 'masters/supplier_form.html'
    permission_required = 'masters.change_supplier'
    success_message = 'Proveedor actualizado exitosamente.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception('Error inesperado al actualizar proveedor %s', self.object.pk)
            form.add_error(None, 'Ocurrió un error inesperado al actualizar el proveedor. Intenta nuevamente.')
            messages.error(self.request, 'No se pudo actualizar el proveedor por un error inesperado.')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('masters:supplier-detail', kwargs={'pk': self.object.pk})


class SupplierDeleteView(StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    """Eliminar proveedor."""

    model = Supplier
    template_name = 'masters/supplier_confirm_delete.html'
    permission_required = 'masters.delete_supplier'
    success_url = reverse_lazy('masters:supplier-list')

    def post(self, request, *args, **kwargs):
        """Implementa soft delete."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=['is_active', 'updated_at'])
        return super().delete(request, *args, **kwargs)
