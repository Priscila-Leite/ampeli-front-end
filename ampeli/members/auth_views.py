from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .services import AmpeliAPIService


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('members:member_list')
    
    def form_valid(self, form):
        """Autenticar via API do Ampeli além do Django"""
        response = super().form_valid(form)
        
        try:
            api_service = AmpeliAPIService()
            # Tentar autenticar via API também
            api_result = api_service.login_user(
                email=form.cleaned_data.get('username'),  # Assumindo que username é email
                password=form.cleaned_data.get('password')
            )
            
            # Armazenar informações da API na sessão
            if api_result.get('success'):
                self.request.session['api_user_id'] = api_result.get('user', {}).get('id')
                self.request.session['api_token'] = api_result.get('token')
                
        except Exception as e:
            # Log do erro mas não impede o login Django
            messages.warning(self.request, 'Conectado localmente, mas houve problema na sincronização com o servidor.')
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Nome de usuário ou senha incorretos.')
        return super().form_invalid(form)


class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('members:member_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        
        # Registrar usuário via API do Ampeli
        try:
            api_service = AmpeliAPIService()
            api_result = api_service.register_user(
                name=user.get_full_name() or user.username,
                email=user.email,
                password=password,
                phone=''
            )
            
            # Armazenar informações da API na sessão
            if api_result.get('success'):
                self.request.session['api_user_id'] = api_result.get('user', {}).get('id')
                self.request.session['api_token'] = api_result.get('token')
                
        except Exception as e:
            messages.warning(self.request, 'Conta criada localmente, mas houve problema na sincronização com o servidor.')
        
        messages.success(self.request, f'Bem-vindo ao Ampeli, {user.first_name or user.username}! Complete seu perfil para uma melhor experiência.')
        return redirect('members:member_onboarding')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


def custom_logout_view(request):
    # Limpar dados da API da sessão
    request.session.pop('api_user_id', None)
    request.session.pop('api_token', None)
    request.session.pop('user_id', None)
    request.session.pop('user_email', None)
    request.session.pop('user_name', None)
    
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('members:login')
