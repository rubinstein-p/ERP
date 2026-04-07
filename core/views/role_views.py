from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from core.forms import RoleForm
from core.services import RoleService
from core.views.mixins import StaffRequiredMixin


class RoleListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Vista para listar roles del sistema.
    """

    model = Group
    template_name = 'core/role_list.html'
    context_object_name = 'roles'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size', '10')
        if page_size in {'10', '25', '50', '100'}:
            return int(page_size)
        return self.paginate_by

    def get_queryset(self):
        search = self.request.GET.get('search', '').strip()
        permission_search = self.request.GET.get('permission_search', '').strip()
        qs = RoleService.get_roles()

        if search:
            qs = qs.filter(name__icontains=search)

        if permission_search:
            qs = qs.filter(
                Q(permissions__name__icontains=permission_search)
                | Q(permissions__codename__icontains=permission_search)
                | Q(permissions__content_type__app_label__icontains=permission_search)
            ).distinct()

        return qs

    def _build_page_window(self, page_obj, window_size=2):
        start = max(page_obj.number - window_size, 1)
        end = min(page_obj.number + window_size, page_obj.paginator.num_pages)
        return list(range(start, end + 1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['permission_search'] = self.request.GET.get('permission_search', '')
        context['page_size'] = self.request.GET.get('page_size', '10')
        context['page_size_options'] = ['10', '25', '50', '100']

        query = self.request.GET.copy()
        query.pop('page', None)
        context['querystring_no_page'] = query.urlencode()

        page_obj = context.get('page_obj')
        if page_obj:
            context['page_window'] = self._build_page_window(page_obj)

        return context


class RoleDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    Vista de detalle de rol.
    """

    model = Group
    template_name = 'core/role_detail.html'
    context_object_name = 'role'

    def get_queryset(self):
        return RoleService.get_roles()


class RoleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Vista para crear roles.
    """

    model = Group
    form_class = RoleForm
    template_name = 'core/role_form.html'
    success_url = reverse_lazy('core:role_list')

    def form_valid(self, form):
        try:
            role = RoleService.create_role(
                name=form.cleaned_data['name'],
                permissions=form.cleaned_data.get('permissions'),
                created_by=self.request.user,
            )
            messages.success(self.request, f'Rol {role.name} creado correctamente')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error al crear rol: {str(e)}')
            return self.form_invalid(form)


class RoleUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Vista para editar roles.
    """

    model = Group
    form_class = RoleForm
    template_name = 'core/role_form.html'
    success_url = reverse_lazy('core:role_list')

    def get_queryset(self):
        return RoleService.get_roles()

    def form_valid(self, form):
        try:
            role = RoleService.update_role(
                role=self.object,
                name=form.cleaned_data['name'],
                permissions=form.cleaned_data.get('permissions'),
                updated_by=self.request.user,
            )
            messages.success(self.request, f'Rol {role.name} actualizado correctamente')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error al actualizar rol: {str(e)}')
            return self.form_invalid(form)


class RoleDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Vista para eliminar roles.
    """

    model = Group
    template_name = 'core/role_confirm_delete.html'
    success_url = reverse_lazy('core:role_list')

    def get_queryset(self):
        return RoleService.get_roles()

    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        try:
            RoleService.delete_role(role, deleted_by=request.user)
            messages.success(request, f'Rol {role.name} eliminado correctamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar rol: {str(e)}')
        return redirect(self.success_url)
