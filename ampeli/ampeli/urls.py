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
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from members.auth_views import CustomLoginView, CustomRegisterView, custom_logout_view

def redirect_to_members(request):
    return redirect('members:member_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_members, name='home'),
    path('members/', include('members.urls')),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('logout/', custom_logout_view, name='logout'),
]
