from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Member, Group, MemberParticipation, AttendanceRecord, InterestArea, MemberInterest
from .services import InChurchAPIService
from .forms import MemberOnboardingForm




@login_required
def member_list(request):
    """Lista de membros com filtros e busca"""
    members = Member.objects.all()
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        members = members.filter(member_status=status_filter)
    
    # Busca
    search_query = request.GET.get('search')
    if search_query:
        members = members.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'member_status_choices': Member.MEMBER_STATUS_CHOICES,
    }
    return render(request, 'members/member_list.html', context)


@login_required
def member_detail(request, member_id):
    """Detalhes de um membro específico"""
    member = get_object_or_404(Member, id=member_id)
    
    # Participações atuais
    current_participations = member.participations.filter(is_current=True).select_related('group')
    
    # Histórico de participações
    past_participations = member.participations.filter(is_current=False).select_related('group')
    
    # Presenças recentes (últimos 3 meses)
    from datetime import datetime, timedelta
    three_months_ago = datetime.now().date() - timedelta(days=90)
    recent_attendances = member.attendances.filter(
        event_date__gte=three_months_ago
    ).order_by('-event_date')[:10]
    
    # Áreas de interesse
    interests = member.interests.select_related('interest_area')
    
    context = {
        'member': member,
        'current_participations': current_participations,
        'past_participations': past_participations,
        'recent_attendances': recent_attendances,
        'interests': interests,
    }
    return render(request, 'members/member_detail.html', context)


@login_required
def member_profile(request, member_id):
    """Perfil completo do membro com todas as informações"""
    member = get_object_or_404(Member, id=member_id)
    
    # Estatísticas de engajamento
    total_attendances = member.attendances.filter(attended=True).count()
    total_events = member.attendances.count()
    attendance_rate = (total_attendances / total_events * 100) if total_events > 0 else 0
    
    # Participações por tipo
    participations_by_type = member.participations.values(
        'group__group_type'
    ).annotate(count=Count('id'))
    
    context = {
        'member': member,
        'attendance_rate': round(attendance_rate, 1),
        'total_attendances': total_attendances,
        'total_events': total_events,
        'participations_by_type': participations_by_type,
    }
    return render(request, 'members/member_profile.html', context)


@login_required
def groups_list(request):
    """Lista de grupos, células e ministérios"""
    groups = Group.objects.filter(is_active=True).annotate(
        member_count=Count('memberparticipation')
    )
    
    # Filtro por tipo
    group_type_filter = request.GET.get('type')
    if group_type_filter:
        groups = groups.filter(group_type=group_type_filter)
    
    context = {
        'groups': groups,
        'group_type_filter': group_type_filter,
        'group_type_choices': Group.GROUP_TYPE_CHOICES,
    }
    return render(request, 'members/groups_list.html', context)


@login_required
def group_detail(request, group_id):
    """Detalhes de um grupo específico"""
    group = get_object_or_404(Group, id=group_id)
    
    # Membros atuais do grupo
    current_members = MemberParticipation.objects.filter(
        group=group, is_current=True
    ).select_related('member')
    
    # Líderes do grupo
    leaders = current_members.filter(role__in=['leader', 'coordinator'])
    
    context = {
        'group': group,
        'current_members': current_members,
        'leaders': leaders,
    }
    return render(request, 'members/group_detail.html', context)


@login_required
@csrf_exempt
def sync_inchurch_data(request):
    """Sincronizar dados com a API do inChurch"""
    if request.method == 'POST':
        try:
            api_service = InChurchAPIService()
            result = api_service.sync_members()
            
            return JsonResponse({
                'success': True,
                'message': f'Sincronização concluída. {result["updated"]} membros atualizados.',
                'data': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro na sincronização: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})




@login_required
def member_onboarding(request):
    """Formulário de onboarding para novos membros"""
    # Verificar se o usuário já tem um perfil de membro
    try:
        member = Member.objects.get(email=request.user.email)
        # Se já tem perfil, redirecionar para lista de membros
        messages.info(request, 'Você já completou seu cadastro!')
        return redirect('members:member_list')
    except Member.DoesNotExist:
        member = None
    
    if request.method == 'POST':
        form = MemberOnboardingForm(request.POST)
        
        if form.is_valid():
            member = form.save(commit=False)
            member.email = request.user.email
            if not member.inchurch_id:
                # Gerar ID único baseado no email e timestamp
                import hashlib
                import time
                unique_string = f"{request.user.email}_{int(time.time())}"
                member.inchurch_id = hashlib.md5(unique_string.encode()).hexdigest()[:20]
            member.save()
            
            messages.success(request, 'Perfil completado com sucesso! Bem-vindo à comunidade!')
            return redirect('members:member_list')
    else:
        form = MemberOnboardingForm()
    
    return render(request, 'members/onboarding.html', {
        'form': form,
        'is_editing': False
    })


@login_required
def check_onboarding_status(request):
    """API endpoint para verificar se usuário completou onboarding"""
    try:
        member = Member.objects.get(email=request.user.email)
        has_completed = True  # Se existe membro, onboarding foi completado
    except Member.DoesNotExist:
        has_completed = False
    
    return JsonResponse({'completed': has_completed})
