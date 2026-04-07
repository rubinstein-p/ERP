from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from core.forms import SystemParameterForm, ParameterSearchForm
from core.models import SystemParameter
from core.services import ParameterService
from core.views.mixins import StaffRequiredMixin


class SystemParameterListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Vista para listar parámetros del sistema.
    """
    model = SystemParameter
    template_name = 'core/parameter_list.html'
    context_object_name = 'parameters'
    paginate_by = 25

    def get_queryset(self):
        queryset = SystemParameter.objects.filter(is_active=True)
        form = ParameterSearchForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get('search')
            category = form.cleaned_data.get('category')
            parameter_type = form.cleaned_data.get('parameter_type')
            is_system = form.cleaned_data.get('is_system')

            if search:
                queryset = queryset.filter(
                    key__icontains=search
                ) | queryset.filter(
                    description__icontains=search
                ) | queryset.filter(
                    category__icontains=search
                )

            if category:
                queryset = queryset.filter(category__icontains=category)

            if parameter_type:
                queryset = queryset.filter(parameter_type=parameter_type)

            if is_system is not None:
                queryset = queryset.filter(is_system=is_system)

        return queryset.order_by('category', 'key')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ParameterSearchForm(self.request.GET)
        return context


class SystemParameterDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    Vista para ver detalles de un parámetro.
    """
    model = SystemParameter
    template_name = 'core/parameter_detail.html'
    context_object_name = 'parameter'

    def get_queryset(self):
        return SystemParameter.objects.filter(is_active=True)


class SystemParameterCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Vista para crear nuevos parámetros.
    """
    model = SystemParameter
    form_class = SystemParameterForm
    template_name = 'core/parameter_form.html'
    success_url = reverse_lazy('core:parameter_list')

    def form_valid(self, form):
        try:
            # Usar el servicio para crear el parámetro
            ParameterService.set_parameter(
                key=form.cleaned_data['key'],
                value=form.cleaned_data['value'],
                parameter_type=form.cleaned_data['parameter_type'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                is_system=form.cleaned_data['is_system'],
                user=self.request.user
            )
            messages.success(self.request, f"Parámetro {form.cleaned_data['key']} creado correctamente")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error al crear parámetro: {str(e)}")
            return self.form_invalid(form)


class SystemParameterUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Vista para editar parámetros.
    """
    model = SystemParameter
    form_class = SystemParameterForm
    template_name = 'core/parameter_form.html'
    success_url = reverse_lazy('core:parameter_list')

    def get_queryset(self):
        return SystemParameter.objects.filter(is_active=True)

    def form_valid(self, form):
        try:
            # Usar el servicio para actualizar el parámetro
            ParameterService.set_parameter(
                key=self.object.key,
                value=form.cleaned_data['value'],
                parameter_type=self.object.parameter_type,  # No se puede cambiar el tipo
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                is_system=form.cleaned_data['is_system'],
                user=self.request.user
            )
            messages.success(self.request, f"Parámetro {self.object.key} actualizado correctamente")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar parámetro: {str(e)}")
            return self.form_invalid(form)


class SystemParameterDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Vista para eliminar parámetros (desactivar).
    """
    model = SystemParameter
    template_name = 'core/parameter_confirm_delete.html'
    success_url = reverse_lazy('core:parameter_list')

    def get_queryset(self):
        return SystemParameter.objects.filter(is_active=True)

    def delete(self, request, *args, **kwargs):
        parameter = self.get_object()
        try:
            ParameterService.delete_parameter(parameter.key, request.user)
            messages.success(request, f"Parámetro {parameter.key} eliminado correctamente")
        except Exception as e:
            messages.error(request, f"Error al eliminar parámetro: {str(e)}")
        return redirect(self.success_url)


class InitializeParametersView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Vista para inicializar parámetros por defecto.
    """
    template_name = 'core/parameter_initialize.html'
    success_url = reverse_lazy('core:parameter_list')

    def get(self, request, *args, **kwargs):
        # Inicializar parámetros por defecto
        ParameterService.initialize_default_parameters()
        messages.success(request, "Parámetros por defecto inicializados correctamente")
        return redirect(self.success_url)