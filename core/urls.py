from django.urls import path

from core.views import (
    HomeView, LoginView, LogoutView, DashboardView,
    UserListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView,
    ProfileView, PasswordChangeView,
    RoleListView, RoleDetailView, RoleCreateView, RoleUpdateView, RoleDeleteView,
    SystemParameterListView, SystemParameterDetailView,
    SystemParameterCreateView, SystemParameterUpdateView, SystemParameterDeleteView,
    InitializeParametersView
)

app_name = 'core'

urlpatterns = [
    # Public
    path('', HomeView.as_view(), name='home'),

    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Usuarios
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Roles y permisos
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/edit/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/delete/', RoleDeleteView.as_view(), name='role_delete'),

    # Perfil de usuario
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/password/', PasswordChangeView.as_view(), name='password_change'),

    # Parámetros del sistema
    path('parameters/', SystemParameterListView.as_view(), name='parameter_list'),
    path('parameters/create/', SystemParameterCreateView.as_view(), name='parameter_create'),
    path('parameters/<int:pk>/', SystemParameterDetailView.as_view(), name='parameter_detail'),
    path('parameters/<int:pk>/edit/', SystemParameterUpdateView.as_view(), name='parameter_update'),
    path('parameters/<int:pk>/delete/', SystemParameterDeleteView.as_view(), name='parameter_delete'),
    path('parameters/initialize/', InitializeParametersView.as_view(), name='parameter_initialize'),
]