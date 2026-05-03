from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from masters.forms import CategoryForm
from masters.models import Category


class CategoryListView(StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    """Lista de categorías."""

    model = Category
    template_name = 'masters/category_list.html'
    paginate_by = 25
    permission_required = 'masters.view_category'

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class CategoryDetailView(StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    """Detalle de categoría."""

    model = Category
    template_name = 'masters/category_detail.html'
    permission_required = 'masters.view_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_active=True)
        return context


class CategoryCreateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, CreateView):
    """Crear categoría."""

    model = Category
    form_class = CategoryForm
    template_name = 'masters/category_form.html'
    permission_required = 'masters.add_category'
    success_url = reverse_lazy('masters:category-list')
    success_message = 'Categoría creada exitosamente.'


class CategoryUpdateView(StaffRequiredMixin, PermissionAuditRequiredMixin, SuccessMessageMixin, UpdateView):
    """Editar categoría."""

    model = Category
    form_class = CategoryForm
    template_name = 'masters/category_form.html'
    permission_required = 'masters.change_category'
    success_message = 'Categoría actualizada exitosamente.'

    def get_success_url(self):
        return reverse_lazy('masters:category-detail', kwargs={'pk': self.object.pk})


class CategoryDeleteView(StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    """Eliminar categoría."""

    model = Category
    template_name = 'masters/category_confirm_delete.html'
    permission_required = 'masters.delete_category'
    success_url = reverse_lazy('masters:category-list')

    def post(self, request, *args, **kwargs):
        """Implementa soft delete."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=['is_active', 'updated_at'])
        return super().delete(request, *args, **kwargs)
