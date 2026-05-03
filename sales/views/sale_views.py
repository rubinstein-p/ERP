from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from sales.forms import SaleForm, SaleItemForm
from sales.models import Sale
from sales.services import SaleService


class SaleListView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    """Listado de ventas con filtros y paginacion."""

    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 25
    permission_required = 'sales.view_sale'
    raise_exception = True

    def get_queryset(self):
        queryset = Sale.objects.filter(is_active=True).select_related('seller')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', 'all').strip()

        if search:
            queryset = queryset.filter(
                Q(sale_number__icontains=search)
                | Q(customer_name__icontains=search)
                | Q(customer_email__icontains=search)
            )

        if status != 'all':
            queryset = queryset.filter(sale_status=status)

        return queryset.order_by('-sale_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'all')
        context['statuses'] = Sale.SALE_STATUS_CHOICES
        return context


class SaleDetailView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    """Detalle de venta."""

    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    permission_required = 'sales.view_sale'
    raise_exception = True

    def get_queryset(self):
        return Sale.objects.filter(is_active=True).select_related('seller').prefetch_related('items')


class SaleCreateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, CreateView):
    """Alta de ventas."""

    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')
    permission_required = 'sales.add_sale'
    raise_exception = True

    def _get_item_formset(self):
        item_formset_cls = formset_factory(SaleItemForm, extra=1, can_delete=True)
        if self.request.method == 'POST' and 'items-TOTAL_FORMS' in self.request.POST:
            return item_formset_cls(self.request.POST, prefix='items')
        return item_formset_cls(prefix='items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_formset'] = kwargs.get('item_formset') or self._get_item_formset()
        return context

    def form_valid(self, form):
        item_formset = self._get_item_formset()
        items_data = []

        if item_formset.is_bound:
            if not item_formset.is_valid():
                return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))

            for item_form in item_formset:
                cleaned = item_form.cleaned_data
                if not cleaned or cleaned.get('DELETE'):
                    continue
                items_data.append(
                    {
                        'product': cleaned.get('product'),
                        'product_name': cleaned.get('product_name'),
                        'quantity': cleaned.get('quantity'),
                        'unit_price': cleaned.get('unit_price'),
                    }
                )

        try:
            sale = SaleService.create_sale(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data.get('customer_email'),
                customer_phone=form.cleaned_data.get('customer_phone'),
                delivery_date=form.cleaned_data.get('delivery_date'),
                notes=form.cleaned_data.get('notes', ''),
                seller=self.request.user,
                items_data=items_data,
            )
            self.object = sale
            messages.success(self.request, f'Venta {sale.sale_number} creada correctamente.')
            return redirect(self.success_url)
        except Exception as exc:
            messages.error(self.request, f'Error al crear venta: {exc}')
            return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))


class SaleUpdateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, UpdateView):
    """Edicion de ventas."""

    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')
    permission_required = 'sales.change_sale'
    raise_exception = True

    def get_queryset(self):
        return Sale.objects.filter(is_active=True)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Venta {self.object.sale_number} actualizada correctamente.')
        return response


class SaleDeleteView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    """Baja logica de ventas."""

    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sale_list')
    permission_required = 'sales.delete_sale'
    raise_exception = True

    def get_queryset(self):
        return Sale.objects.filter(is_active=True)

    def post(self, request, *args, **kwargs):
        sale = self.get_object()
        try:
            SaleService.soft_delete_sale(sale=sale, user=request.user)
            messages.success(request, f'Venta {sale.sale_number} eliminada correctamente.')
        except Exception as exc:
            messages.error(request, f'Error al eliminar venta: {exc}')
        return redirect(self.success_url)
