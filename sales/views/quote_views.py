from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from core.views.mixins import PermissionAuditRequiredMixin, StaffRequiredMixin
from sales.forms.quote_form import QuoteForm, QuoteItemForm
from sales.models.quote import Quote
from sales.services.quote_service import QuoteService


class QuoteListView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, ListView):
    model = Quote
    template_name = 'sales/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 25
    permission_required = 'sales.view_quote'
    raise_exception = True

    def get_queryset(self):
        queryset = Quote.objects.filter(is_active=True).select_related('seller')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', 'all').strip()

        if search:
            queryset = queryset.filter(
                Q(quote_number__icontains=search)
                | Q(customer_name__icontains=search)
                | Q(customer_email__icontains=search)
            )
        if status != 'all':
            queryset = queryset.filter(quote_status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'all')
        context['statuses'] = Quote.QUOTE_STATUS_CHOICES
        return context


class QuoteDetailView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DetailView):
    model = Quote
    template_name = 'sales/quote_detail.html'
    context_object_name = 'quote'
    permission_required = 'sales.view_quote'
    raise_exception = True

    def get_queryset(self):
        return Quote.objects.filter(is_active=True).select_related('seller').prefetch_related('items')


class QuoteCreateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'sales/quote_form.html'
    success_url = reverse_lazy('sales:quote_list')
    permission_required = 'sales.add_quote'
    raise_exception = True

    def _get_item_formset(self):
        item_formset_cls = formset_factory(QuoteItemForm, extra=1, can_delete=True)
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
            quote = QuoteService.create_quote(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data.get('customer_email'),
                customer_phone=form.cleaned_data.get('customer_phone', ''),
                valid_until=form.cleaned_data.get('valid_until'),
                notes=form.cleaned_data.get('notes', ''),
                seller=self.request.user,
                items_data=items_data,
            )
            self.object = quote
            messages.success(self.request, f'Presupuesto {quote.quote_number} creado correctamente.')
            return redirect(self.success_url)
        except Exception as exc:
            messages.error(self.request, f'Error al crear presupuesto: {exc}')
            return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))


class QuoteUpdateView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'sales/quote_form.html'
    success_url = reverse_lazy('sales:quote_list')
    permission_required = 'sales.change_quote'
    raise_exception = True

    def get_queryset(self):
        return Quote.objects.filter(is_active=True)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Presupuesto {self.object.quote_number} actualizado correctamente.')
        return response


class QuoteDeleteView(LoginRequiredMixin, StaffRequiredMixin, PermissionAuditRequiredMixin, DeleteView):
    model = Quote
    template_name = 'sales/quote_confirm_delete.html'
    success_url = reverse_lazy('sales:quote_list')
    permission_required = 'sales.delete_quote'
    raise_exception = True

    def get_queryset(self):
        return Quote.objects.filter(is_active=True)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        try:
            QuoteService.soft_delete_quote(quote, request.user)
            messages.success(request, f'Presupuesto {quote.quote_number} eliminado correctamente.')
        except Exception as exc:
            messages.error(request, f'Error al eliminar presupuesto: {exc}')
        return redirect(self.success_url)


class QuoteConvertToOrderView(LoginRequiredMixin, StaffRequiredMixin, View):
    """Convierte un presupuesto en un pedido."""

    def post(self, request, pk, *args, **kwargs):
        quote = get_object_or_404(Quote, pk=pk, is_active=True)
        try:
            order = QuoteService.convert_to_order(quote, request.user)
            messages.success(request, f'Presupuesto convertido al pedido {order.order_number} correctamente.')
            return redirect('sales:order_detail', pk=order.pk)
        except Exception as exc:
            messages.error(request, f'Error al convertir presupuesto: {exc}')
            return redirect('sales:quote_detail', pk=pk)
