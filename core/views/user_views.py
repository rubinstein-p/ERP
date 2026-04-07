from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
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


class UserListView(LoginRequiredMixin, ListView):
    """
    Vista para listar usuarios.
    """
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        queryset = UserService.get_active_users()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        return queryset


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver detalles de un usuario.
    """
    model = User
    template_name = 'core/user_detail.html'
    context_object_name = 'user_profile'

    def get_queryset(self):
        return UserService.get_active_users()


class UserCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevos usuarios.
    """
    model = User
    form_class = UserCreationForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

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
            )
            messages.success(self.request, f"Usuario {user.username} creado correctamente")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error al crear usuario: {str(e)}")
            return self.form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar usuarios.
    """
    model = User
    form_class = UserChangeForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

    def get_queryset(self):
        return UserService.get_active_users()

    def form_valid(self, form):
        try:
            user = UserService.update_user(
                self.object,
                **{k: v for k, v in form.cleaned_data.items()
                   if k not in ['password1', 'password2']}
            )
            messages.success(self.request, f"Usuario {user.username} actualizado correctamente")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar usuario: {str(e)}")
            return self.form_invalid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
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