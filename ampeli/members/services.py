import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Member, Group, InterestArea, MemberParticipation, AttendanceRecord


class InChurchAPIService:
    """Serviço para integração com a API do inChurch"""
    
    def __init__(self):
        # Configurações da API - devem ser definidas no settings.py
        self.base_url = getattr(settings, 'INCHURCH_API_URL', 'https://api.inchurch.com.br')
        self.api_key = getattr(settings, 'INCHURCH_API_KEY', '')
        self.church_id = getattr(settings, 'INCHURCH_CHURCH_ID', '')
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_members(self, page=1, limit=100):
        """Buscar membros da API do inChurch"""
        try:
            url = f"{self.base_url}/members"
            params = {
                'church_id': self.church_id,
                'page': page,
                'limit': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar membros da API: {str(e)}")
    
    def get_member_details(self, inchurch_member_id):
        """Buscar detalhes específicos de um membro"""
        try:
            url = f"{self.base_url}/members/{inchurch_member_id}"
            params = {'church_id': self.church_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar detalhes do membro: {str(e)}")
    
    def get_member_participations(self, inchurch_member_id):
        """Buscar participações de um membro em grupos/ministérios"""
        try:
            url = f"{self.base_url}/members/{inchurch_member_id}/participations"
            params = {'church_id': self.church_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar participações: {str(e)}")
    
    def get_member_attendance(self, inchurch_member_id, start_date=None, end_date=None):
        """Buscar histórico de presenças de um membro"""
        try:
            url = f"{self.base_url}/members/{inchurch_member_id}/attendance"
            params = {'church_id': self.church_id}
            
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar presenças: {str(e)}")
    
    def sync_members(self):
        """Sincronizar todos os membros com a API do inChurch"""
        updated_count = 0
        created_count = 0
        errors = []
        
        try:
            page = 1
            has_more = True
            
            while has_more:
                api_data = self.get_members(page=page)
                members_data = api_data.get('data', [])
                
                if not members_data:
                    has_more = False
                    break
                
                for member_data in members_data:
                    try:
                        member, created = self._update_or_create_member(member_data)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    except Exception as e:
                        errors.append(f"Erro ao processar membro {member_data.get('id', 'unknown')}: {str(e)}")
                
                # Verificar se há mais páginas
                has_more = api_data.get('has_next_page', False)
                page += 1
            
            return {
                'updated': updated_count,
                'created': created_count,
                'errors': errors
            }
        
        except Exception as e:
            raise Exception(f"Erro na sincronização: {str(e)}")
    
    def _update_or_create_member(self, member_data):
        """Atualizar ou criar um membro baseado nos dados da API"""
        inchurch_id = str(member_data.get('id'))
        
        # Mapear campos da API para o modelo
        member_fields = {
            'inchurch_id': inchurch_id,
            'full_name': member_data.get('full_name', ''),
            'gender': member_data.get('gender', ''),
            'phone': member_data.get('phone', ''),
            'email': member_data.get('email', ''),
            'address': member_data.get('address', ''),
            'neighborhood': member_data.get('neighborhood', ''),
            'marital_status': member_data.get('marital_status', ''),
            'member_status': self._map_member_status(member_data.get('status')),
            'availability_notes': member_data.get('availability', ''),
            'gifts_aptitudes': member_data.get('gifts', ''),
            'prayer_requests': member_data.get('prayer_requests', ''),
            'testimonies': member_data.get('testimonies', ''),
        }
        
        # Tratar data de nascimento
        birth_date_str = member_data.get('birth_date')
        if birth_date_str:
            try:
                member_fields['birth_date'] = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Tratar data de entrada
        entry_date_str = member_data.get('entry_date')
        if entry_date_str:
            try:
                member_fields['entry_date'] = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Tratar última atividade
        last_activity_str = member_data.get('last_activity')
        if last_activity_str:
            try:
                member_fields['last_activity'] = datetime.strptime(last_activity_str, '%Y-%m-%d %H:%M:%S')
                member_fields['last_activity'] = timezone.make_aware(member_fields['last_activity'])
            except ValueError:
                pass
        
        # Calcular score de engajamento baseado nos dados
        member_fields['engagement_score'] = self._calculate_engagement_score(member_data)
        
        # Atualizar ou criar membro
        member, created = Member.objects.update_or_create(
            inchurch_id=inchurch_id,
            defaults=member_fields
        )
        
        # Sincronizar áreas de interesse
        self._sync_member_interests(member, member_data.get('interests', []))
        
        # Sincronizar participações em grupos
        self._sync_member_participations(member, member_data.get('participations', []))
        
        return member, created
    
    def _map_member_status(self, api_status):
        """Mapear status da API para o modelo local"""
        status_mapping = {
            'active': 'active',
            'inactive': 'inactive',
            'visitor': 'visitor',
            'ativo': 'active',
            'inativo': 'inactive',
            'visitante': 'visitor'
        }
        return status_mapping.get(api_status, 'visitor')
    
    def _calculate_engagement_score(self, member_data):
        """Calcular score de engajamento baseado nos dados da API"""
        score = 0
        
        # Presença recente
        if member_data.get('recent_attendance_count', 0) > 0:
            score += min(member_data.get('recent_attendance_count', 0) * 10, 50)
        
        # Participação em grupos
        if member_data.get('active_participations', 0) > 0:
            score += min(member_data.get('active_participations', 0) * 20, 40)
        
        # Voluntariado
        if member_data.get('volunteer_areas'):
            score += 10
        
        return min(score, 100)
    
    def _sync_member_interests(self, member, interests_data):
        """Sincronizar áreas de interesse do membro"""
        # Limpar interesses existentes
        member.interests.all().delete()
        
        for interest_data in interests_data:
            interest_name = interest_data.get('name', '')
            if interest_name:
                interest_area, _ = InterestArea.objects.get_or_create(
                    name=interest_name,
                    defaults={'description': interest_data.get('description', '')}
                )
                
                from .models import MemberInterest
                MemberInterest.objects.create(
                    member=member,
                    interest_area=interest_area,
                    level=interest_data.get('level', 1)
                )
    
    def _sync_member_participations(self, member, participations_data):
        """Sincronizar participações do membro em grupos"""
        for participation_data in participations_data:
            group_name = participation_data.get('group_name', '')
            if group_name:
                group, _ = Group.objects.get_or_create(
                    name=group_name,
                    defaults={
                        'group_type': participation_data.get('group_type', 'group'),
                        'description': participation_data.get('description', ''),
                        'is_active': participation_data.get('is_active', True)
                    }
                )
                
                # Verificar se já existe participação
                participation, created = MemberParticipation.objects.get_or_create(
                    member=member,
                    group=group,
                    defaults={
                        'role': participation_data.get('role', 'member'),
                        'start_date': self._parse_date(participation_data.get('start_date')),
                        'end_date': self._parse_date(participation_data.get('end_date')),
                        'is_current': participation_data.get('is_current', True)
                    }
                )
                
                if not created:
                    # Atualizar participação existente
                    participation.role = participation_data.get('role', participation.role)
                    participation.end_date = self._parse_date(participation_data.get('end_date'))
                    participation.is_current = participation_data.get('is_current', participation.is_current)
                    participation.save()
    
    def _parse_date(self, date_str):
        """Converter string de data para objeto date"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
