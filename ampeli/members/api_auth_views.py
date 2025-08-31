from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from .services import AmpeliAPIService
from .forms import CustomAuthenticationForm, CustomUserCreationForm
import json


class APILoginView(View):
    """View de login baseada apenas na API do Ampeli"""
    template_name = 'registration/login.html'
    
    def get(self, request):
        # Se já está logado, redirecionar
        if request.session.get('api_user_id'):
            return redirect('members:member_list')
        
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        email = request.POST.get('username')  # Usando 'username' do form padrão
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios.')
            form = CustomAuthenticationForm()
            return render(request, self.template_name, {'form': form})
        
        api_service = AmpeliAPIService()
        result = api_service.login_user(email=email, password=password)
        
        if result.get('success'):
            # Armazenar informações da API na sessão
            user_data = result.get('user', {})
            request.session['api_user_id'] = user_data.get('id')
            request.session['api_token'] = result.get('token')
            request.session['user_email'] = user_data.get('email')
            request.session['user_name'] = user_data.get('name')
            
            messages.success(request, f'Bem-vindo, {user_data.get("name", "usuário")}!')
            return redirect('members:member_list')
        else:
            # Tratar erros específicos da API
            error_type = result.get('error', 'UNKNOWN')
            error_message = result.get('message', 'Erro desconhecido')
            
            if error_type == 'INVALID_CREDENTIALS':
                messages.error(request, 'Email ou senha incorretos.')
            elif error_type == 'USER_NOT_FOUND':
                messages.error(request, 'Usuário não encontrado.')
            elif error_type in ['SERVICE_UNAVAILABLE', 'CONNECTION_ERROR']:
                messages.error(request, 'Serviço temporariamente indisponível. Tente novamente.')
            else:
                messages.error(request, f'Erro no login: {error_message}')
            
            form = CustomAuthenticationForm()
            return render(request, self.template_name, {'form': form})


class APIRegisterView(View):
    """View de registro baseada apenas na API do Ampeli"""
    template_name = 'registration/register.html'
    
    def get(self, request):
        # Se já está logado, redirecionar
        if request.session.get('api_user_id'):
            return redirect('members:member_list')
        
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        name = request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', '')
        name = name.strip() or request.POST.get('username', '')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password_confirm = request.POST.get('password2')
        
        # Validações básicas
        if not all([name, email, password, password_confirm]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            form = CustomUserCreationForm()
            return render(request, self.template_name, {'form': form})
        
        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
            form = CustomUserCreationForm()
            return render(request, self.template_name, {'form': form})
        
        api_service = AmpeliAPIService()
        result = api_service.register_user(name=name, email=email, password=password)
        
        if result.get('success'):
            # Fazer login automático após registro
            login_result = api_service.login_user(email=email, password=password)
            
            if login_result.get('success'):
                user_data = login_result.get('user', {})
                request.session['api_user_id'] = user_data.get('id')
                request.session['api_token'] = login_result.get('token')
                request.session['user_email'] = user_data.get('email')
                request.session['user_name'] = user_data.get('name')
                
                messages.success(request, f'Bem-vindo ao Ampeli, {user_data.get("name", "usuário")}!')
                messages.info(request, 'Complete seu perfil para uma melhor experiência!')
                return redirect('members:member_onboarding')
            else:
                messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
                return redirect('members:login')
        else:
            # Tratar erros específicos da API
            error_type = result.get('error', 'UNKNOWN')
            error_message = result.get('message', 'Erro desconhecido')
            
            if error_type == 'USER_EXISTS':
                messages.error(request, 'Este email já está cadastrado.')
            elif error_type == 'INVALID_EMAIL':
                messages.error(request, 'Formato de email inválido.')
            elif error_type == 'WEAK_PASSWORD':
                messages.error(request, 'Senha muito fraca. Use pelo menos 6 caracteres.')
            elif error_type in ['SERVICE_UNAVAILABLE', 'CONNECTION_ERROR']:
                messages.error(request, 'Serviço temporariamente indisponível. Tente novamente.')
            else:
                messages.error(request, f'Erro no cadastro: {error_message}')
            
            form = CustomUserCreationForm()
            return render(request, self.template_name, {'form': form})


def api_logout_view(request):
    """Logout baseado apenas em sessão"""
    # Limpar dados da API da sessão
    request.session.pop('api_user_id', None)
    request.session.pop('api_token', None)
    request.session.pop('user_id', None)
    request.session.pop('user_email', None)
    request.session.pop('user_name', None)
    
    # Limpar toda a sessão
    request.session.flush()
    
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('members:login')


def login_required_api(view_func):
    """Decorator para verificar se usuário está logado via API"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('api_user_id'):
            messages.warning(request, 'Você precisa fazer login para acessar esta página.')
            return redirect('members:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
def register_user_api(request):
    """API endpoint para registro de usuário"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validação dos dados recebidos
            required_fields = ['name', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': 'VALIDATION_ERROR',
                        'message': f'Campo {field} é obrigatório'
                    })
            
            api_service = AmpeliAPIService()
            result = api_service.register_user(
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                phone=data.get('phone', '')
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'INVALID_JSON',
                'message': 'Formato JSON inválido'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'UNEXPECTED_ERROR',
                'message': f'Erro inesperado: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'METHOD_NOT_ALLOWED',
        'message': 'Método não permitido'
    })


@csrf_exempt
def login_user_api(request):
    """API endpoint para login de usuário"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validação dos dados recebidos
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'VALIDATION_ERROR',
                    'message': 'Email e senha são obrigatórios'
                })
            
            api_service = AmpeliAPIService()
            result = api_service.login_user(email=email, password=password)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'INVALID_JSON',
                'message': 'Formato JSON inválido'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'UNEXPECTED_ERROR',
                'message': f'Erro inesperado: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'METHOD_NOT_ALLOWED',
        'message': 'Método não permitido'
    })
