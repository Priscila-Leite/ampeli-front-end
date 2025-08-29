from django.contrib import admin
from .models import (
    Member, InterestArea, MemberInterest, Group, 
    MemberParticipation, AttendanceRecord
)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'member_status', 'email', 'phone', 'entry_date', 'engagement_score']
    list_filter = ['member_status', 'gender', 'marital_status', 'event_preference']
    search_fields = ['full_name', 'email', 'phone', 'inchurch_id']
    readonly_fields = ['inchurch_id', 'created_at', 'updated_at', 'age']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('full_name', 'gender', 'birth_date', 'age', 'marital_status')
        }),
        ('Contato', {
            'fields': ('email', 'phone', 'address', 'neighborhood')
        }),
        ('Status e Participação', {
            'fields': ('member_status', 'entry_date', 'last_attendance', 'event_preference')
        }),
        ('Engajamento', {
            'fields': ('last_activity', 'engagement_score', 'availability_notes')
        }),
        ('Informações Extras', {
            'fields': ('gifts_aptitudes', 'prayer_requests', 'testimonies'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('inchurch_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(InterestArea)
class InterestAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(MemberInterest)
class MemberInterestAdmin(admin.ModelAdmin):
    list_display = ['member', 'interest_area', 'level']
    list_filter = ['interest_area', 'level']
    search_fields = ['member__full_name', 'interest_area__name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'is_active']
    list_filter = ['group_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(MemberParticipation)
class MemberParticipationAdmin(admin.ModelAdmin):
    list_display = ['member', 'group', 'role', 'start_date', 'is_current']
    list_filter = ['role', 'is_current', 'group__group_type']
    search_fields = ['member__full_name', 'group__name']
    date_hierarchy = 'start_date'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['member', 'event_name', 'event_type', 'event_date', 'attended']
    list_filter = ['event_type', 'attended', 'event_date']
    search_fields = ['member__full_name', 'event_name']
    date_hierarchy = 'event_date'
