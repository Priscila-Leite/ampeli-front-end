from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Member


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome de usuário'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Primeiro nome'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Sobrenome'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'E-mail'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome de usuário'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })


class MemberOnboardingForm(forms.ModelForm):
    """Formulário completo de onboarding para novos membros"""
    
    # Campos adicionais não no modelo
    terms_accepted = forms.BooleanField(
        required=True,
        label="Aceito os termos e condições da igreja"
    )
    
    class Meta:
        model = Member
        fields = [
            'full_name', 'birth_date', 'gender', 'marital_status',
            'phone', 'email', 'contact_preference', 'address', 'neighborhood',
            'church_attendance_time', 'previous_churches', 'church_discovery', 'church_discovery_other',
            'previous_participation', 'volunteer_interest', 'volunteer_areas',
            'available_days', 'available_times', 'event_preference',
            'community_interests', 'seeking_in_church', 'open_to_new_groups', 'group_preferences',
            'faith_stage', 'pastoral_care_interest', 'faith_challenges',
            'gifts_aptitudes'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'contact_preference': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Endereço completo'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            
            'church_attendance_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 6 meses, 2 anos, primeira vez'}),
            'previous_churches': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Quais igrejas frequentou anteriormente?'}),
            'church_discovery': forms.Select(attrs={'class': 'form-select'}),
            'church_discovery_other': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique como conheceu a igreja'}),
            
            'previous_participation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Grupos, ministérios, cursos que já participou'}),
            'volunteer_areas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Louvor, ensino, ação social, recepção, mídia, etc.'}),
            
            'available_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Domingos, quartas-feiras'}),
            'available_times': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Manhã, noite, fins de semana'}),
            'event_preference': forms.Select(attrs={'class': 'form-select'}),
            
            'community_interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Discipulado, comunidade, cursos, evangelismo'}),
            'seeking_in_church': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Crescimento espiritual, amizades, servir, apoio, etc.'}),
            'group_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Preferências por faixas etárias, temas específicos'}),
            
            'faith_stage': forms.Select(attrs={'class': 'form-select'}),
            'faith_challenges': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dificuldades que enfrenta na caminhada cristã'}),
            'gifts_aptitudes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Habilidades ou dons que gostaria de compartilhar'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos obrigatórios
        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        
        # Labels personalizados
        self.fields['volunteer_interest'].label = "Pretende se voluntariar?"
        self.fields['open_to_new_groups'].label = "Está disposto a participar de novos grupos?"
        self.fields['pastoral_care_interest'].label = "Interessado em acompanhamento pastoral individual?"
        
        # Adicionar classes CSS aos campos boolean
        self.fields['volunteer_interest'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['open_to_new_groups'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['pastoral_care_interest'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['terms_accepted'].widget.attrs.update({'class': 'form-check-input'})
    
    def save(self, commit=True):
        member = super().save(commit=False)
        member.member_status = 'new'
        member.onboarding_completed = True
        if commit:
            member.save()
        return member
