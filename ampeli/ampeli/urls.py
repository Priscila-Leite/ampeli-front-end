"""
URL configuration for ampeli project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.shortcuts import redirect
from members.api_auth_views import APILoginView, APIRegisterView, api_logout_view

def redirect_to_members(request):
    return redirect('members:member_list')

urlpatterns = [
    path('', redirect_to_members, name='home'),
    path('members/', include('members.urls')),
    
    # Authentication URLs (API-based)
    path('login/', APILoginView.as_view(), name='login'),
    path('register/', APIRegisterView.as_view(), name='register'),
    path('logout/', api_logout_view, name='logout'),
]
