# Ampeli - Sistema de Gestão de Membros

Sistema Django para gestão de membros da igreja com integração à API inChurch.

## Funcionalidades

### 📊 Dashboard
- Visão geral dos membros (ativos, inativos, visitantes)
- Estatísticas de engajamento
- Grupos mais ativos
- Gráficos interativos

### 👥 Gestão de Membros
- Lista completa de membros com filtros e busca
- Perfis detalhados com informações demográficas
- Histórico de participação em grupos/ministérios
- Registro de presenças em eventos
- Áreas de interesse e dons espirituais

### 🔄 Integração inChurch API
- Sincronização automática de dados
- Mapeamento completo dos campos prioritários:
  - **Dados Demográficos**: nome, gênero, idade, estado civil, contato
  - **Participação**: status, grupos, ministérios, voluntariado
  - **Preferências**: áreas de interesse, disponibilidade
  - **Engajamento**: frequência, atividades recentes

## Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Configuração

1. **Clone o repositório**
```bash
git clone <repository-url>
cd ampeli-front-end-1/ampeli
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure a API inChurch**
Edite o arquivo `ampeli/settings.py`:
```python
INCHURCH_API_URL = 'https://api.inchurch.com.br/v1'
INCHURCH_API_KEY = 'sua_chave_api_aqui'
INCHURCH_CHURCH_ID = 'id_da_sua_igreja'
```

4. **Execute as migrações**
```bash
py manage.py makemigrations
py manage.py migrate
```

5. **Crie um superusuário**
```bash
py manage.py createsuperuser
```

6. **Execute o servidor**
```bash
py manage.py runserver
```

## Uso

### Acessando o Sistema
- **Frontend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

### Sincronização com inChurch
1. Acesse o dashboard
2. Clique em "Sincronizar inChurch"
3. Aguarde a conclusão da sincronização

### Navegação
- **Dashboard**: Visão geral e estatísticas
- **Membros**: Lista e detalhes dos membros
- **Grupos**: Gestão de células, ministérios e grupos
- **Analytics**: Relatórios e análises

## Estrutura dos Dados

### Modelos Principais

#### Member (Membro)
- Informações pessoais e demográficas
- Dados de contato
- Status de participação
- Score de engajamento
- Preferências e disponibilidade

#### Group (Grupo/Ministério)
- Células, ministérios, cursos
- Tipos e descrições
- Status ativo/inativo

#### MemberParticipation (Participação)
- Relacionamento membro-grupo
- Funções e períodos
- Histórico de participações

#### AttendanceRecord (Presença)
- Registro de presenças em eventos
- Tipos de eventos
- Histórico de frequência

## API inChurch - Campos Mapeados

### Dados Prioritários Sincronizados:

**Perfil Demográfico:**
- Nome completo
- Gênero
- Data de nascimento/idade
- Estado civil
- Telefone, e-mail
- Endereço e bairro

**Participação & Engajamento:**
- Status do membro
- Data de entrada
- Presença em eventos
- Grupos/ministérios atuais
- Histórico de voluntariado

**Preferências:**
- Áreas de interesse
- Disponibilidade
- Preferência presencial/online
- Cursos realizados

**Indicadores:**
- Score de engajamento
- Última atividade
- Frequência recente
- Sinais de afastamento

## Tecnologias

- **Backend**: Django 5.2.5
- **Frontend**: Bootstrap 5.3, Chart.js
- **Database**: SQLite (desenvolvimento)
- **API**: Requests para integração inChurch
- **UI**: Font Awesome, CSS moderno

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## Suporte

Para suporte e dúvidas sobre a integração com inChurch API, consulte:
- Documentação oficial da API inChurch
- Issues do projeto
- Contato com a equipe de desenvolvimento
