from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Member, Group, InterestArea, MemberParticipation, AttendanceRecord
from .services import InChurchAPIService


def dashboard(request):
    """Dashboard principal com estatísticas dos membros"""
    total_members = Member.objects.count()
    active_members = Member.objects.filter(member_status='active').count()
    inactive_members = Member.objects.filter(member_status='inactive').count()
    visitors = Member.objects.filter(member_status='visitor').count()
    
    # Membros recentes (últimos 30 dias)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_members = Member.objects.filter(entry_date__gte=thirty_days_ago).count()
    
    # Grupos mais ativos
    active_groups = Group.objects.filter(is_active=True).annotate(
        member_count=Count('memberparticipation')
    ).order_by('-member_count')[:5]
    
    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'visitors': visitors,
        'recent_members': recent_members,
        'active_groups': active_groups,
    }
    return render(request, 'members/dashboard.html', context)


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


def analytics(request):
    """Página de analytics e relatórios"""
    # Distribuição por status
    status_distribution = Member.objects.values('member_status').annotate(
        count=Count('id')
    )
    
    # Distribuição por faixa etária
    from datetime import datetime
    current_year = datetime.now().year
    age_ranges = {
        '0-17': 0, '18-25': 0, '26-35': 0, '36-50': 0, '51-65': 0, '65+': 0
    }
    
    for member in Member.objects.filter(birth_date__isnull=False):
        age = member.age
        if age is not None:
            if age <= 17:
                age_ranges['0-17'] += 1
            elif age <= 25:
                age_ranges['18-25'] += 1
            elif age <= 35:
                age_ranges['26-35'] += 1
            elif age <= 50:
                age_ranges['36-50'] += 1
            elif age <= 65:
                age_ranges['51-65'] += 1
            else:
                age_ranges['65+'] += 1
    
    # Engajamento por mês (últimos 12 meses)
    from datetime import datetime, timedelta
    twelve_months_ago = datetime.now().date() - timedelta(days=365)
    monthly_engagement = AttendanceRecord.objects.filter(
        event_date__gte=twelve_months_ago,
        attended=True
    ).extra(
        select={'month': "strftime('%%Y-%%m', event_date)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    context = {
        'status_distribution': status_distribution,
        'age_ranges': age_ranges,
        'monthly_engagement': list(monthly_engagement),
    }
    return render(request, 'members/analytics.html', context)
