from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member
from .forms import MemberOnboardingForm
from .services import AmpeliAPIService
from .api_auth_views import login_required_api
import json




@login_required_api
def member_list(request):
    """Lista de membros com filtros e busca via API"""
    api_service = AmpeliAPIService()
    
    try:
        # Buscar todos os membros via API
        members_data = api_service.get_all_members()
        
        # Aplicar filtros localmente (idealmente seria na API)
        status_filter = request.GET.get('status')
        search_query = request.GET.get('search')
        
        if status_filter:
            members_data = [m for m in members_data if m.get('memberStatus') == status_filter]
        
        if search_query:
            members_data = [
                m for m in members_data 
                if search_query.lower() in m.get('fullName', '').lower() or
                   search_query.lower() in m.get('email', '').lower() or
                   search_query.lower() in m.get('phone', '').lower()
            ]
        
        # Simular paginação
        from django.core.paginator import Paginator
        paginator = Paginator(members_data, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'search_query': search_query,
            'member_status_choices': [('active', 'Ativo'), ('inactive', 'Inativo'), ('visitor', 'Visitante')],
        }
    except Exception as e:
        messages.error(request, f'Erro ao carregar membros: {str(e)}')
        context = {
            'page_obj': None,
            'status_filter': None,
            'search_query': None,
            'member_status_choices': [],
        }
    
    return render(request, 'members/member_list.html', context)


@login_required_api
def member_detail(request, member_id):
    """Detalhes de um membro específico via API"""
    api_service = AmpeliAPIService()
    
    try:
        # Buscar membro via API
        member_data = api_service.get_member_by_id(member_id)
        
        if not member_data:
            messages.error(request, 'Membro não encontrado.')
            return redirect('members:member_list')
        
        context = {
            'member': member_data,
            'current_participations': member_data.get('currentParticipations', []),
            'past_participations': member_data.get('pastParticipations', []),
            'recent_attendances': member_data.get('recentAttendances', []),
            'interests': member_data.get('interests', []),
        }
    except Exception as e:
        messages.error(request, f'Erro ao carregar detalhes do membro: {str(e)}')
        return redirect('members:member_list')
    
    return render(request, 'members/member_detail.html', context)


@login_required_api
def member_profile(request, member_id):
    """Perfil completo do membro com todas as informações via API"""
    api_service = AmpeliAPIService()
    
    try:
        # Buscar membro via API
        member_data = api_service.get_member_by_id(member_id)
        
        if not member_data:
            messages.error(request, 'Membro não encontrado.')
            return redirect('members:member_list')
        
        context = {
            'member': member_data,
            'attendance_rate': member_data.get('attendanceRate', 0),
            'total_attendances': member_data.get('totalAttendances', 0),
            'total_events': member_data.get('totalEvents', 0),
            'participations_by_type': member_data.get('participationsByType', []),
        }
    except Exception as e:
        messages.error(request, f'Erro ao carregar perfil do membro: {str(e)}')
        return redirect('members:member_list')
    
    return render(request, 'members/member_profile.html', context)


@login_required_api
def groups_list(request):
    """Lista de grupos, células e ministérios via API"""
    # Placeholder - implementar quando API de grupos estiver disponível
    groups = []
    
    # Filtro por tipo
    group_type_filter = request.GET.get('type')
    
    context = {
        'groups': groups,
        'group_type_filter': group_type_filter,
        'group_type_choices': [],
    }
    return render(request, 'members/groups_list.html', context)


@login_required_api
def group_detail(request, group_id):
    """Detalhes de um grupo específico via API"""
    # Placeholder - implementar quando API de grupos estiver disponível
    context = {
        'group': None,
        'current_members': [],
        'leaders': [],
    }
    return render(request, 'members/group_detail.html', context)


@csrf_exempt
def register_user_api(request):
    """Registrar usuário via API do Ampeli"""
    if request.method == 'POST':
        try:
            import json
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
            
            # Retornar resultado direto do serviço (já inclui tratamento de erro)
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
    """Login de usuário via API do Ampeli"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            # Validação dos dados recebidos
            required_fields = ['email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': 'VALIDATION_ERROR',
                        'message': f'Campo {field} é obrigatório'
                    })
            
            api_service = AmpeliAPIService()
            result = api_service.login_user(
                email=data.get('email'),
                password=data.get('password')
            )
            
            # Armazenar informações do usuário na sessão se login bem-sucedido
            if result.get('success'):
                request.session['api_user_id'] = result.get('user', {}).get('id')
                request.session['api_token'] = result.get('token')
                request.session['user_email'] = result.get('user', {}).get('email')
                request.session['user_name'] = result.get('user', {}).get('name')
            
            # Retornar resultado direto do serviço (já inclui tratamento de erro)
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




@login_required_api
def member_onboarding(request):
    """Formulário de onboarding para novos membros"""
    api_service = AmpeliAPIService()
    
    # Verificar se o usuário já tem um perfil de membro via API
    try:
        user_email = request.session.get('user_email')
        if user_email:
            member_data = api_service.get_member_by_email(user_email)
            if member_data:
                messages.info(request, 'Você já completou seu cadastro!')
                return redirect('members:member_list')
    except Exception:
        # Se não encontrou membro, continua com o onboarding
        pass
    
    if request.method == 'POST':
        form = MemberOnboardingForm(request.POST)
        
        if form.is_valid():
            try:
                # Obter ID do usuário da API da sessão
                user_id = request.session.get('api_user_id')
                if not user_id:
                    messages.error(request, 'Sessão expirada. Faça login novamente.')
                    return redirect('members:login')
                
                # Formatar dados para a API
                member_data = api_service.format_member_data_for_api(form.cleaned_data, user_id)
                
                # Validar dados
                if api_service.validate_member_data(member_data):
                    # Criar membro via API
                    result = api_service.create_member(member_data)
                    
                    messages.success(request, 'Perfil completado com sucesso! Bem-vindo à comunidade!')
                    return redirect('members:member_list')
                else:
                    messages.error(request, 'Dados inválidos. Verifique os campos obrigatórios.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar perfil: {str(e)}')
    else:
        form = MemberOnboardingForm()
    
    return render(request, 'members/onboarding.html', {
        'form': form,
        'is_editing': False
    })


@login_required_api
def check_onboarding_status(request):
    """API endpoint para verificar se usuário completou onboarding"""
    try:
        api_service = AmpeliAPIService()
        user_email = request.session.get('user_email')
        if user_email:
            member_data = api_service.get_member_by_email(user_email)
            has_completed = bool(member_data)
        else:
            has_completed = False
    except Exception:
        has_completed = False
    
    return JsonResponse({'completed': has_completed})
