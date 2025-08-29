from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Membros
    path('membros/', views.member_list, name='member_list'),
    path('membros/<int:member_id>/', views.member_detail, name='member_detail'),
    path('membros/<int:member_id>/perfil/', views.member_profile, name='member_profile'),
    
    # Grupos
    path('grupos/', views.groups_list, name='groups_list'),
    path('grupos/<int:group_id>/', views.group_detail, name='group_detail'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # API
    path('api/sync-inchurch/', views.sync_inchurch_data, name='sync_inchurch'),
]
