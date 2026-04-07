from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import FormView

from core.forms import (
    UserCreationForm, UserChangeForm, UserProfileForm,
    PasswordChangeForm, LoginForm
)
from core.models import User
from core.services import UserService
from core.views.mixins import StaffRequiredMixin


class HomeView(TemplateView):
    """
    Vista pública de inicio.
    """
    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)


class LoginView(FormView):
    """
    Vista para el inicio de sesión de usuarios.
    """
    template_name = 'core/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = UserService.authenticate_user(username, password)

        if user:
            login(self.request, user)
            if not form.cleaned_data.get('remember_me'):
                self.request.session.set_expiry(0)
            messages.success(self.request, f"Bienvenido, {user.get_full_name() or user.username}")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Credenciales inválidas")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)


class LogoutView(LoginRequiredMixin, FormView):
    """
    Vista para cerrar sesión.
    """

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Sesión cerrada correctamente")
        return redirect('core:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista del dashboard principal.
    """
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
            'recent_activity': [],  # TODO: Implementar actividad reciente
        })
        return context


class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Vista para listar usuarios.
    """
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('groups', 'user_permissions')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status', 'active')

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(employee_id__icontains=search)
            )

        return queryset.order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'active')
        return context


class UserDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    Vista para ver detalles de un usuario.
    """
    model = User
    template_name = 'core/user_detail.html'
    context_object_name = 'user_profile'

    def get_queryset(self):
        return User.objects.all().prefetch_related('groups', 'user_permissions')


class UserCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Vista para crear nuevos usuarios.
    """
    model = User
    form_class = UserCreationForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            user = UserService.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                phone=form.cleaned_data.get('phone'),
                department=form.cleaned_data.get('department'),
                employee_id=form.cleaned_data.get('employee_id'),
                is_active=form.cleaned_data.get('is_active', True),
                is_staff=form.cleaned_data.get('is_staff', False),
                is_superuser=form.cleaned_data.get('is_superuser', False),
                groups=form.cleaned_data.get('groups'),
                user_permissions=form.cleaned_data.get('user_permissions'),
                created_by=self.request.user,
            )
            self.object = user
            messages.success(self.request, f"Usuario {user.username} creado correctamente")
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error al crear usuario: {str(e)}")
            return self.form_invalid(form)


class UserUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Vista para editar usuarios.
    """
    model = User
    form_class = UserChangeForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

    def get_queryset(self):
        return User.objects.all().prefetch_related('groups', 'user_permissions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            user = UserService.update_user(
                self.object,
                **{k: v for k, v in form.cleaned_data.items() if k not in ['password1', 'password2']},
                updated_by=self.request.user,
            )
            self.object = user
            messages.success(self.request, f"Usuario {user.username} actualizado correctamente")
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error al actualizar usuario: {str(e)}")
            return self.form_invalid(form)


class UserDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Vista para eliminar usuarios (desactivar).
    """
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('core:user_list')

    def get_queryset(self):
        return UserService.get_active_users()

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            UserService.deactivate_user(user, request.user)
            messages.success(request, f"Usuario {user.username} desactivado correctamente")
        except Exception as e:
            messages.error(request, f"Error al desactivar usuario: {str(e)}")
        return redirect(self.success_url)


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    Vista para que los usuarios editen su perfil.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente")
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, FormView):
    """
    Vista para cambio de contraseña.
    """
    template_name = 'core/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('core:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Contraseña cambiada correctamente")
        return super().form_valid(form)