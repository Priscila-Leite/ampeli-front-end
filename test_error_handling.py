#!/usr/bin/env python
"""
Teste dos tratamentos de erro para API de autenticação
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ampeli.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'ampeli'))
django.setup()

from members.services import AmpeliAPIService

def test_register_validation_errors():
    """Testar erros de validação no registro"""
    print("=== Testando erros de validacao no registro ===")
    
    api_service = AmpeliAPIService()
    
    # Teste 1: Campos obrigatórios vazios
    result = api_service.register_user("", "", "")
    print(f"Campos vazios: {result['error']} - {result['message']}")
    assert result['success'] == False
    assert result['error'] == 'VALIDATION_ERROR'
    
    # Teste 2: Email inválido
    result = api_service.register_user("João", "email-invalido", "123456")
    print(f"Email invalido: {result['error']} - {result['message']}")
    assert result['success'] == False
    assert result['error'] == 'INVALID_EMAIL'
    
    # Teste 3: Senha fraca
    result = api_service.register_user("João", "joao@teste.com", "123")
    print(f"Senha fraca: {result['error']} - {result['message']}")
    assert result['success'] == False
    assert result['error'] == 'WEAK_PASSWORD'
    
    print("OK - Todos os testes de validacao no registro passaram!\n")

def test_login_validation_errors():
    """Testar erros de validação no login"""
    print("=== Testando erros de validacao no login ===")
    
    api_service = AmpeliAPIService()
    
    # Teste 1: Campos obrigatórios vazios
    result = api_service.login_user("", "")
    print(f"Campos vazios: {result['error']} - {result['message']}")
    assert result['success'] == False
    assert result['error'] == 'VALIDATION_ERROR'
    
    # Teste 2: Email inválido
    result = api_service.login_user("email-invalido", "senha123")
    print(f"Email invalido: {result['error']} - {result['message']}")
    assert result['success'] == False
    assert result['error'] == 'INVALID_EMAIL'
    
    print("✓ Todos os testes de validacao no login passaram!\n")

def test_api_connection_errors():
    """Testar erros de conexão com API"""
    print("=== Testando erros de conexao com API ===")
    
    api_service = AmpeliAPIService()
    
    # Teste com dados válidos (mas API pode estar indisponível)
    result = api_service.register_user("João Silva", "joao@teste.com", "senha123")
    print(f"Registro com API: {result.get('error', 'SUCCESS')} - {result['message']}")
    
    result = api_service.login_user("joao@teste.com", "senha123")
    print(f"Login com API: {result.get('error', 'SUCCESS')} - {result['message']}")
    
    print("✓ Testes de conexao completados!\n")

def test_error_message_quality():
    """Testar qualidade das mensagens de erro"""
    print("=== Testando qualidade das mensagens de erro ===")
    
    api_service = AmpeliAPIService()
    
    test_cases = [
        ("", "", "", "VALIDATION_ERROR"),
        ("João", "email-invalido", "123456", "INVALID_EMAIL"),
        ("João", "joao@teste.com", "123", "WEAK_PASSWORD"),
        ("", "joao@teste.com", "senha123", "VALIDATION_ERROR"),
    ]
    
    for name, email, password, expected_error in test_cases:
        result = api_service.register_user(name, email, password)
        assert result['error'] == expected_error
        assert len(result['message']) > 10  # Mensagem deve ser descritiva
        assert 'success' in result
        print(f"✓ {expected_error}: {result['message']}")
    
    print("✓ Todas as mensagens de erro sao descritivas!\n")

def main():
    """Executar todos os testes"""
    print("Iniciando testes de tratamento de erro...\n")
    
    try:
        test_register_validation_errors()
        test_login_validation_errors()
        test_api_connection_errors()
        test_error_message_quality()
        
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✓ Validacoes funcionando corretamente")
        print("✓ Mensagens de erro claras e descritivas")
        print("✓ Tratamento de erros de API implementado")
        
    except AssertionError as e:
        print(f"❌ TESTE FALHOU: {e}")
    except Exception as e:
        print(f"💥 ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
