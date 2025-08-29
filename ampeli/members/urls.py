from django.urls import path
from . import views
from .auth_views import CustomLoginView, CustomRegisterView, custom_logout_view

app_name = 'members'

urlpatterns = [
    # Membros
    path('', views.member_list, name='member_list'),
    path('membros/', views.member_list, name='member_list_alt'),
    path('membros/<int:member_id>/', views.member_detail, name='member_detail'),
    path('membros/<int:member_id>/perfil/', views.member_profile, name='member_profile'),
    
    # Onboarding
    path('onboarding/', views.member_onboarding, name='member_onboarding'),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('logout/', custom_logout_view, name='logout'),
    
    # Grupos
    path('grupos/', views.groups_list, name='groups_list'),
    path('grupos/<int:group_id>/', views.group_detail, name='group_detail'),
    
    # API
    path('api/sync-inchurch/', views.sync_inchurch_data, name='sync_inchurch'),
    path('api/check-onboarding/', views.check_onboarding_status, name='check_onboarding_status'),
]
