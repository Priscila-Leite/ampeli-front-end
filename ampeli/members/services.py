import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional, Any

import logging
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)



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

            logger.info(f"Registering user on: {self.base_url}/auth/register")    
            logger.debug(f"Registering user: {data}")
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
        try:
            logger.info(f"Checking user status for ID: {user_id}")
            return self._make_request('GET', f'/auth/status/{user_id}')
        except Exception as e:
            logger.error(f"Error checking user status: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao verificar status do usuário'
            }
    
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
        try:
            data = {
                "userId": user_id,
                "currentPassword": current_password,
                "newPassword": new_password
            }
            logger.info(f"Changing password for user ID: {user_id}")
            return self._make_request('POST', '/auth/change-password', data)
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao alterar senha'
            }
    
    # ==================== USUÁRIOS ====================
    
    def get_all_users(self) -> List[Dict]:
        """Listar todos os usuários"""
        try:
            logger.info("Fetching all users")
            return self._make_request('GET', '/users')
        except Exception as e:
            logger.error(f"Error fetching all users: {str(e)}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Dict:
        """Buscar usuário por ID"""
        try:
            logger.info(f"Fetching user by ID: {user_id}")
            return self._make_request('GET', f'/users/{user_id}')
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Dict:
        """Buscar usuário por email"""
        try:
            logger.info(f"Fetching user by email: {email}")
            return self._make_request('GET', f'/users/email/{email}')
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {str(e)}")
            return None
    
    def create_user(self, name: str, email: str, password: str, phone: str = None) -> Dict:
        """Criar novo usuário"""
        try:
            data = {
                "name": name,
                "email": email,
                "password": password
            }
            if phone:
                data["phone"] = phone
            
            logger.info(f"Creating user: {email}")
            return self._make_request('POST', '/users', data)
        except Exception as e:
            logger.error(f"Error creating user {email}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao criar usuário'
            }
    
    def update_user(self, user_id: int, name: str, email: str, phone: str = None, password: str = None) -> Dict:
        """Atualizar usuário existente"""
        try:
            data = {
                "name": name,
                "email": email
            }
            if phone:
                data["phone"] = phone
            if password:
                data["password"] = password
            
            logger.info(f"Updating user ID: {user_id}")
            return self._make_request('PUT', f'/users/{user_id}', data)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao atualizar usuário'
            }
    
    def delete_user(self, user_id: int) -> Dict:
        """Remover usuário"""
        try:
            logger.info(f"Deleting user ID: {user_id}")
            return self._make_request('DELETE', f'/users/{user_id}')
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao remover usuário'
            }
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Autenticar usuário (método alternativo)"""
        try:
            data = {
                "email": email,
                "password": password
            }
            logger.info(f"Authenticating user: {email}")
            return self._make_request('POST', '/users/authenticate', data)
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro na autenticação'
            }
    
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
        try:
            logger.info(f"Fetching member by ID: {member_id}")
            return self._make_request('GET', f'/members/{member_id}')
        except Exception as e:
            logger.error(f"Error fetching member by ID {member_id}: {str(e)}")
            return None
    
    def get_member_by_user_id(self, user_id: int) -> Dict:
        """Buscar membro por ID do usuário"""
        try:
            logger.info(f"Fetching member by user ID: {user_id}")
            return self._make_request('GET', f'/members/user/{user_id}')
        except Exception as e:
            logger.error(f"Error fetching member by user ID {user_id}: {str(e)}")
            return None
    
    def get_member_by_email(self, email: str) -> Dict:
        """Buscar membro por email"""
        try:
            return self._make_request('GET', f'/members/email/{email}')
        except Exception:
            # Se a API não estiver disponível ou membro não encontrado, retornar None
            return None
    
    def get_members_by_faith_stage(self, faith_stage: str) -> List[Dict]:
        """Buscar membros por estágio da fé"""
        try:
            logger.info(f"Fetching members by faith stage: {faith_stage}")
            return self._make_request('GET', f'/members/faith-stage/{faith_stage}')
        except Exception as e:
            logger.error(f"Error fetching members by faith stage {faith_stage}: {str(e)}")
            return []
    
    def get_members_by_interest(self, interest: str) -> List[Dict]:
        """Buscar membros por área de interesse"""
        try:
            logger.info(f"Fetching members by interest: {interest}")
            return self._make_request('GET', f'/members/interest/{interest}')
        except Exception as e:
            logger.error(f"Error fetching members by interest {interest}: {str(e)}")
            return []
    
    def get_members_by_volunteer_area(self, area: str) -> List[Dict]:
        """Buscar membros por área de voluntariado"""
        try:
            logger.info(f"Fetching members by volunteer area: {area}")
            return self._make_request('GET', f'/members/volunteer-area/{area}')
        except Exception as e:
            logger.error(f"Error fetching members by volunteer area {area}: {str(e)}")
            return []
    
    def create_member(self, member_data: Dict) -> Dict:
        """Criar novo membro"""
        try:
            logger.info(f"Creating member: {member_data.get('fullName', 'Unknown')}")
            logger.debug(f"Member data: {member_data}")
            return self._make_request('POST', '/members', member_data)
        except Exception as e:
            logger.error(f"Error creating member: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao criar membro'
            }
    
    def update_member(self, member_id: int, member_data: Dict) -> Dict:
        """Atualizar membro existente"""
        try:
            logger.info(f"Updating member ID: {member_id}")
            logger.debug(f"Member data: {member_data}")
            return self._make_request('PUT', f'/members/{member_id}', member_data)
        except Exception as e:
            logger.error(f"Error updating member {member_id}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao atualizar membro'
            }
    
    def delete_member(self, member_id: int) -> Dict:
        """Remover membro"""
        try:
            logger.info(f"Deleting member ID: {member_id}")
            return self._make_request('DELETE', f'/members/{member_id}')
        except Exception as e:
            logger.error(f"Error deleting member {member_id}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao remover membro'
            }
    
    # ==================== RECOMENDAÇÕES ====================
    
    def get_member_recommendations(self, member_id: int) -> Dict:
        """Gerar recomendações para um membro específico"""
        try:
            logger.info(f"Getting recommendations for member ID: {member_id}")
            return self._make_request('POST', f'/recommendations/member/{member_id}')
        except Exception as e:
            logger.error(f"Error getting recommendations for member {member_id}: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao gerar recomendações'
            }
    
    def get_custom_recommendations(self, recommendation_data: Dict) -> Dict:
        """Gerar recomendações customizadas"""
        try:
            logger.info("Getting custom recommendations")
            logger.debug(f"Recommendation data: {recommendation_data}")
            return self._make_request('POST', '/recommendations/custom', recommendation_data)
        except Exception as e:
            logger.error(f"Error getting custom recommendations: {str(e)}")
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': 'Erro ao gerar recomendações customizadas'
            }
    
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
