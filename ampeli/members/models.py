from django.db import models
from django.utils import timezone


class Member(models.Model):
    """Modelo para armazenar dados dos membros da igreja via API inChurch"""
    
    # Dados demográficos e de contato
    full_name = models.CharField(max_length=200, verbose_name="Nome Completo")
    gender = models.CharField(max_length=20, blank=True, verbose_name="Gênero")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    marital_status = models.CharField(max_length=50, blank=True, verbose_name="Estado Civil")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    address = models.TextField(blank=True, verbose_name="Endereço")
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name="Bairro")
    
    # Histórico de participação
    MEMBER_STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('visitor', 'Visitante'),
    ]
    member_status = models.CharField(max_length=20, choices=MEMBER_STATUS_CHOICES, default='visitor', verbose_name="Status do Membro")
    entry_date = models.DateField(null=True, blank=True, verbose_name="Data de Entrada")
    last_attendance = models.DateField(null=True, blank=True, verbose_name="Última Presença")
    
    # Preferências
    PREFERENCE_CHOICES = [
        ('presencial', 'Presencial'),
        ('online', 'Online'),
        ('ambos', 'Ambos'),
    ]
    event_preference = models.CharField(max_length=20, choices=PREFERENCE_CHOICES, default='presencial', verbose_name="Preferência de Eventos")
    availability_notes = models.TextField(blank=True, verbose_name="Disponibilidade")
    
    # Indicadores de engajamento
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="Última Atividade")
    engagement_score = models.IntegerField(default=0, verbose_name="Score de Engajamento")
    
    # Dados extras
    gifts_aptitudes = models.TextField(blank=True, verbose_name="Dons e Aptidões")
    prayer_requests = models.TextField(blank=True, verbose_name="Pedidos de Oração")
    testimonies = models.TextField(blank=True, verbose_name="Testemunhos")
    
    # Metadados
    inchurch_id = models.CharField(max_length=100, unique=True, verbose_name="ID inChurch")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


class InterestArea(models.Model):
    """Áreas de interesse dos membros"""
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Área de Interesse"
        verbose_name_plural = "Áreas de Interesse"
    
    def __str__(self):
        return self.name


class MemberInterest(models.Model):
    """Relacionamento entre membros e áreas de interesse"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='interests')
    interest_area = models.ForeignKey(InterestArea, on_delete=models.CASCADE)
    level = models.IntegerField(default=1, verbose_name="Nível de Interesse (1-5)")
    
    class Meta:
        unique_together = ['member', 'interest_area']
        verbose_name = "Interesse do Membro"
        verbose_name_plural = "Interesses dos Membros"


class Group(models.Model):
    """Grupos, células e ministérios"""
    name = models.CharField(max_length=200, verbose_name="Nome")
    GROUP_TYPE_CHOICES = [
        ('cell', 'Célula'),
        ('ministry', 'Ministério'),
        ('course', 'Curso'),
        ('group', 'Grupo'),
    ]
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
    
    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"


class MemberParticipation(models.Model):
    """Participação dos membros em grupos"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='participations')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('member', 'Membro'),
        ('leader', 'Líder'),
        ('coordinator', 'Coordenador'),
        ('volunteer', 'Voluntário'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="Função")
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    is_current = models.BooleanField(default=True, verbose_name="Participação Atual")
    
    class Meta:
        verbose_name = "Participação"
        verbose_name_plural = "Participações"
    
    def __str__(self):
        return f"{self.member.full_name} - {self.group.name} ({self.get_role_display()})"


class AttendanceRecord(models.Model):
    """Registro de presenças em eventos/cultos"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    event_name = models.CharField(max_length=200, verbose_name="Nome do Evento")
    event_date = models.DateField(verbose_name="Data do Evento")
    EVENT_TYPE_CHOICES = [
        ('service', 'Culto'),
        ('cell', 'Célula'),
        ('course', 'Curso'),
        ('event', 'Evento Especial'),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name="Tipo de Evento")
    attended = models.BooleanField(default=True, verbose_name="Compareceu")
    
    class Meta:
        verbose_name = "Registro de Presença"
        verbose_name_plural = "Registros de Presença"
        unique_together = ['member', 'event_name', 'event_date']
    
    def __str__(self):
        status = "Presente" if self.attended else "Ausente"
        return f"{self.member.full_name} - {self.event_name} ({status})"
