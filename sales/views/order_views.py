from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from sales.forms.order_form import OrderForm, OrderItemForm
from sales.models.order import Order, OrderItem
from sales.services.order_service import OrderService


class OrderListView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    model = Order
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    paginate_by = 25
    permission_required = 'sales.view_order'
    raise_exception = True

    def get_queryset(self):
        queryset = Order.objects.filter(is_active=True).select_related('seller', 'quote')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', 'all').strip()

        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search)
                | Q(customer_name__icontains=search)
                | Q(customer_email__icontains=search)
            )
        if status != 'all':
            queryset = queryset.filter(order_status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'all')
        context['statuses'] = Order.ORDER_STATUS_CHOICES
        return context


class OrderDetailView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    model = Order
    template_name = 'sales/order_detail.html'
    context_object_name = 'order'
    permission_required = 'sales.view_order'
    raise_exception = True

    def get_queryset(self):
        return Order.objects.filter(is_active=True).select_related('seller', 'quote').prefetch_related('items')


class OrderCreateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('sales:order_list')
    permission_required = 'sales.add_order'
    raise_exception = True

    def _get_item_formset(self):
        item_formset_cls = formset_factory(OrderItemForm, extra=1, can_delete=True)
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
            order = OrderService.create_order(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data.get('customer_email'),
                customer_phone=form.cleaned_data.get('customer_phone', ''),
                expected_delivery=form.cleaned_data.get('expected_delivery'),
                notes=form.cleaned_data.get('notes', ''),
                seller=self.request.user,
                items_data=items_data,
            )
            self.object = order
            messages.success(self.request, f'Pedido {order.order_number} creado correctamente.')
            return redirect(self.success_url)
        except Exception as exc:
            messages.error(self.request, f'Error al crear pedido: {exc}')
            return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))


class OrderUpdateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('sales:order_list')
    permission_required = 'sales.change_order'
    raise_exception = True

    def get_queryset(self):
        return Order.objects.filter(is_active=True)

    def _get_item_formset(self):
        item_formset_cls = formset_factory(OrderItemForm, extra=1, can_delete=True)
        if self.request.method == 'POST' and 'items-TOTAL_FORMS' in self.request.POST:
            return item_formset_cls(self.request.POST, prefix='items')

        initial = [
            {
                'product': item.product,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
            }
            for item in self.object.items.filter(is_active=True)
        ]
        return item_formset_cls(prefix='items', initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_formset'] = kwargs.get('item_formset') or self._get_item_formset()
        return context

    def form_valid(self, form):
        item_formset = self._get_item_formset()
        if item_formset.is_bound and not item_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))

        response = super().form_valid(form)

        # Reemplaza los items activos por los enviados en el formulario.
        self.object.items.filter(is_active=True).update(is_active=False)

        if item_formset.is_bound:
            for item_form in item_formset:
                cleaned = item_form.cleaned_data
                if not cleaned or cleaned.get('DELETE'):
                    continue

                product = cleaned.get('product')
                OrderItem.objects.create(
                    order=self.object,
                    product=product,
                    product_name=product.name,
                    quantity=cleaned.get('quantity'),
                    unit_price=cleaned.get('unit_price'),
                )

        self.object.calculate_totals()
        messages.success(self.request, f'Pedido {self.object.order_number} actualizado correctamente.')
        return response


class OrderDeleteView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    model = Order
    template_name = 'sales/order_confirm_delete.html'
    success_url = reverse_lazy('sales:order_list')
    permission_required = 'sales.delete_order'
    raise_exception = True

    def get_queryset(self):
        return Order.objects.filter(is_active=True)

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        try:
            OrderService.soft_delete_order(order, request.user)
            messages.success(request, f'Pedido {order.order_number} eliminado correctamente.')
        except Exception as exc:
            messages.error(request, f'Error al eliminar pedido: {exc}')
        return redirect(self.success_url)


class OrderConvertToSaleView(LoginRequiredMixin, StaffRequiredMixin, View):
    """Convierte un pedido en una venta."""

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, is_active=True)
        try:
            sale = OrderService.convert_to_sale(order, request.user)
            messages.success(request, f'Pedido convertido a la venta {sale.sale_number} correctamente.')
            return redirect('sales:sale_detail', pk=sale.pk)
        except Exception as exc:
            messages.error(request, f'Error al convertir pedido: {exc}')
            return redirect('sales:order_detail', pk=pk)
