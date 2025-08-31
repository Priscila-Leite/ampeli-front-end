from django.urls import path
from . import views
from .api_auth_views import APILoginView, APIRegisterView, api_logout_view, register_user_api, login_user_api

app_name = 'members'

urlpatterns = [
    # Membros
    path('', views.member_list, name='member_list'),
    path('membros/', views.member_list, name='member_list_alt'),
    path('membros/<int:member_id>/', views.member_detail, name='member_detail'),
    path('membros/<int:member_id>/perfil/', views.member_profile, name='member_profile'),
    
    # Onboarding
    path('onboarding/', views.member_onboarding, name='member_onboarding'),
    
    # Authentication URLs (API-based)
    path('login/', APILoginView.as_view(), name='login'),
    path('register/', APIRegisterView.as_view(), name='register'),
    path('logout/', api_logout_view, name='logout'),
    
    # Grupos
    path('grupos/', views.groups_list, name='groups_list'),
    path('grupos/<int:group_id>/', views.group_detail, name='group_detail'),
    
    # API
    path('api/register/', register_user_api, name='register_user_api'),
    path('api/login/', login_user_api, name='login_user_api'),
    path('api/check-onboarding/', views.check_onboarding_status, name='check_onboarding_status'),
]
