import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional, Any


class AmpeliAPIService:
    """Serviço para integração com a API do Ampeli"""
    
    def __init__(self):
        self.base_url = 'https://ampeli-backend.onrender.com/api'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Método auxiliar para fazer requisições HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição para {url}: {str(e)}")
    
    # ==================== AUTENTICAÇÃO ====================
    
    def register_user(self, name: str, email: str, password: str, phone: str = None) -> Dict:
        """Registrar novo usuário com tratamento de erros"""
        try:
            # Validações básicas
            if not name or not email or not password:
                return {
                    'success': False,
                    'error': 'VALIDATION_ERROR',
                    'message': 'Nome, email e senha são obrigatórios'
                }
            
            if '@' not in email or '.' not in email:
                return {
                    'success': False,
                    'error': 'INVALID_EMAIL',
                    'message': 'Formato de email inválido'
                }
            
            if len(password) < 6:
                return {
                    'success': False,
                    'error': 'WEAK_PASSWORD',
                    'message': 'Senha deve ter pelo menos 6 caracteres'
                }
            
            data = {
                "name": name,
                "email": email,
                "password": password
            }
            if phone:
                data["phone"] = phone
                
            result = self._make_request('POST', '/auth/register', data)
            return {
                'success': True,
                'user': result.get('user', {}),
                'token': result.get('token', ''),
                'message': 'Usuário registrado com sucesso'
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Tratamento específico por tipo de erro
            if '409' in error_msg or 'conflict' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'USER_EXISTS',
                    'message': 'Este email já está cadastrado'
                }
            elif '400' in error_msg or 'bad request' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'INVALID_DATA',
                    'message': 'Dados inválidos fornecidos'
                }
            elif '503' in error_msg or 'service unavailable' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'SERVICE_UNAVAILABLE',
                    'message': 'Serviço temporariamente indisponível. Tente novamente em alguns minutos.'
                }
            elif '500' in error_msg or 'internal server error' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'SERVER_ERROR',
                    'message': 'Erro interno do servidor. Tente novamente mais tarde.'
                }
            else:
                return {
                    'success': False,
                    'error': 'CONNECTION_ERROR',
                    'message': 'Erro de conexão. Verifique sua internet e tente novamente.'
                }
    
    def login_user(self, email: str, password: str) -> Dict:
        """Login de usuário com tratamento de erros"""
        try:
            # Validações básicas
            if not email or not password:
                return {
                    'success': False,
                    'error': 'VALIDATION_ERROR',
                    'message': 'Email e senha são obrigatórios'
                }
            
            if '@' not in email or '.' not in email:
                return {
                    'success': False,
                    'error': 'INVALID_EMAIL',
                    'message': 'Formato de email inválido'
                }
            
            data = {
                "email": email,
                "password": password
            }
            
            result = self._make_request('POST', '/auth/login', data)
            return {
                'success': True,
                'user': result.get('user', {}),
                'token': result.get('token', ''),
                'message': 'Login realizado com sucesso'
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Tratamento específico por tipo de erro
            if '401' in error_msg or 'unauthorized' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'INVALID_CREDENTIALS',
                    'message': 'Email ou senha incorretos'
                }
            elif '404' in error_msg or 'not found' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'USER_NOT_FOUND',
                    'message': 'Usuário não encontrado'
                }
            elif '429' in error_msg or 'too many requests' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'RATE_LIMITED',
                    'message': 'Muitas tentativas de login. Tente novamente em alguns minutos.'
                }
            elif '503' in error_msg or 'service unavailable' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'SERVICE_UNAVAILABLE',
                    'message': 'Serviço temporariamente indisponível. Tente novamente em alguns minutos.'
                }
            elif '500' in error_msg or 'internal server error' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'SERVER_ERROR',
                    'message': 'Erro interno do servidor. Tente novamente mais tarde.'
                }
            else:
                return {
                    'success': False,
                    'error': 'CONNECTION_ERROR',
                    'message': 'Erro de conexão. Verifique sua internet e tente novamente.'
                }
    
    def check_user_status(self, user_id: int) -> Dict:
        """Verificar status do usuário"""
        return self._make_request('GET', f'/auth/status/{user_id}')
    
    def check_email_availability(self, email: str) -> bool:
        """Verificar disponibilidade do email"""
        try:
            result = self._make_request('GET', f'/auth/check-email/{email}')
            return result.get('available', False)
        except Exception:
            # Se a API não estiver disponível, assumir que o email está disponível
            return True
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict:
        """Alterar senha do usuário"""
        data = {
            "userId": user_id,
            "currentPassword": current_password,
            "newPassword": new_password
        }
        return self._make_request('POST', '/auth/change-password', data)
    
    # ==================== USUÁRIOS ====================
    
    def get_all_users(self) -> List[Dict]:
        """Listar todos os usuários"""
        return self._make_request('GET', '/users')
    
    def get_user_by_id(self, user_id: int) -> Dict:
        """Buscar usuário por ID"""
        return self._make_request('GET', f'/users/{user_id}')
    
    def get_user_by_email(self, email: str) -> Dict:
        """Buscar usuário por email"""
        return self._make_request('GET', f'/users/email/{email}')
    
    def create_user(self, name: str, email: str, password: str, phone: str = None) -> Dict:
        """Criar novo usuário"""
        data = {
            "name": name,
            "email": email,
            "password": password
        }
        if phone:
            data["phone"] = phone
            
        return self._make_request('POST', '/users', data)
    
    def update_user(self, user_id: int, name: str, email: str, phone: str = None, password: str = None) -> Dict:
        """Atualizar usuário existente"""
        data = {
            "name": name,
            "email": email
        }
        if phone:
            data["phone"] = phone
        if password:
            data["password"] = password
            
        return self._make_request('PUT', f'/users/{user_id}', data)
    
    def delete_user(self, user_id: int) -> Dict:
        """Remover usuário"""
        return self._make_request('DELETE', f'/users/{user_id}')
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Autenticar usuário (método alternativo)"""
        data = {
            "email": email,
            "password": password
        }
        return self._make_request('POST', '/users/authenticate', data)
    
    def user_exists(self, email: str) -> bool:
        """Verificar se email já existe"""
        try:
            result = self._make_request('GET', f'/users/exists/{email}')
            return result.get('exists', False)
        except Exception:
            # Se a API não estiver disponível, assumir que o usuário não existe
            return False
    
    # ==================== MEMBROS ====================
    
    def get_all_members(self) -> List[Dict]:
        """Listar todos os membros"""
        try:
            return self._make_request('GET', '/members')
        except Exception:
            # Se a API não estiver disponível, retornar lista vazia
            return []
    
    def get_member_by_id(self, member_id: int) -> Dict:
        """Buscar membro por ID"""
        return self._make_request('GET', f'/members/{member_id}')
    
    def get_member_by_user_id(self, user_id: int) -> Dict:
        """Buscar membro por ID do usuário"""
        return self._make_request('GET', f'/members/user/{user_id}')
    
    def get_member_by_email(self, email: str) -> Dict:
        """Buscar membro por email"""
        try:
            return self._make_request('GET', f'/members/email/{email}')
        except Exception:
            # Se a API não estiver disponível ou membro não encontrado, retornar None
            return None
    
    def get_members_by_faith_stage(self, faith_stage: str) -> List[Dict]:
        """Buscar membros por estágio da fé"""
        return self._make_request('GET', f'/members/faith-stage/{faith_stage}')
    
    def get_members_by_interest(self, interest: str) -> List[Dict]:
        """Buscar membros por área de interesse"""
        return self._make_request('GET', f'/members/interest/{interest}')
    
    def get_members_by_volunteer_area(self, area: str) -> List[Dict]:
        """Buscar membros por área de voluntariado"""
        return self._make_request('GET', f'/members/volunteer-area/{area}')
    
    def create_member(self, member_data: Dict) -> Dict:
        """Criar novo membro"""
        return self._make_request('POST', '/members', member_data)
    
    def update_member(self, member_id: int, member_data: Dict) -> Dict:
        """Atualizar membro existente"""
        return self._make_request('PUT', f'/members/{member_id}', member_data)
    
    def delete_member(self, member_id: int) -> Dict:
        """Remover membro"""
        return self._make_request('DELETE', f'/members/{member_id}')
    
    # ==================== RECOMENDAÇÕES ====================
    
    def get_member_recommendations(self, member_id: int) -> Dict:
        """Gerar recomendações para um membro específico"""
        return self._make_request('POST', f'/recommendations/member/{member_id}')
    
    def get_custom_recommendations(self, recommendation_data: Dict) -> Dict:
        """Gerar recomendações customizadas"""
        return self._make_request('POST', '/recommendations/custom', recommendation_data)
    
    def check_recommendations_health(self) -> Dict:
        """Verificar saúde do serviço LLM"""
        try:
            return self._make_request('GET', '/recommendations/health')
        except Exception as e:
            # Retornar status de erro se a API não estiver disponível
            return {'status': 'error', 'message': str(e)}
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def format_member_data_for_api(self, form_data: Dict, user_id: int) -> Dict:
        """Formatar dados do formulário para o formato da API"""
        return {
            "user": {"id": user_id},
            "fullName": form_data.get('full_name', ''),
            "birthDate": form_data.get('birth_date', ''),
            "gender": form_data.get('gender', ''),
            "maritalStatus": form_data.get('marital_status', ''),
            "email": form_data.get('email', ''),
            "phone": form_data.get('phone', ''),
            "churchAttendanceTime": form_data.get('church_attendance_time', ''),
            "previousChurches": form_data.get('previous_churches', ''),
            "howFoundChurch": form_data.get('church_discovery', ''),
            "previousParticipation": form_data.get('previous_participation', ''),
            "interestAreas": form_data.get('volunteer_areas', ''),
            "skillsGifts": form_data.get('gifts_aptitudes', ''),
            "volunteerArea": form_data.get('volunteer_areas', ''),
            "availableDaysTimes": f"{form_data.get('available_days', '')} - {form_data.get('available_times', '')}",
            "eventPreference": form_data.get('event_preference', ''),
            "interestsIn": form_data.get('community_interests', ''),
            "churchSearch": form_data.get('seeking_in_church', ''),
            "openToNewGroups": form_data.get('open_to_new_groups', False),
            "groupPreference": form_data.get('group_preferences', ''),
            "faithStage": form_data.get('faith_stage', ''),
            "pastoralSupportInterest": form_data.get('pastoral_care_interest', False),
            "faithDifficulties": form_data.get('faith_challenges', '')
        }
    
    def validate_member_data(self, member_data: Dict) -> bool:
        """Validar dados do membro antes de enviar para a API"""
        required_fields = ['fullName', 'email']
        
        for field in required_fields:
            if not member_data.get(field):
                return False
        
        # Validar formato de email
        email = member_data.get('email', '')
        if '@' not in email or '.' not in email:
            return False
            
        return True
    
    def format_date_for_api(self, date_obj) -> str:
        """Formatar data para o formato esperado pela API"""
        if not date_obj:
            return ''
        
        if isinstance(date_obj, str):
            return date_obj
            
        return date_obj.strftime('%Y-%m-%d')
    
    def parse_api_response_error(self, response_data: Dict) -> str:
        """Extrair mensagem de erro da resposta da API"""
        if isinstance(response_data, dict):
            return response_data.get('message', response_data.get('error', 'Erro desconhecido'))
        return str(response_data)
