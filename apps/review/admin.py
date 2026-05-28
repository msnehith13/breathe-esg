from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AnalystFlag, AuditLog


@admin.register(AnalystFlag)
class AnalystFlagAdmin(admin.ModelAdmin):
    list_display = ['id', 'normalized_record', 'flagged_by', 'resolved', 'created_at']
    list_filter = ['resolved']
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'org', 'actor', 'action', 'timestamp']
    list_filter = ['action', 'org']
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        return False  # Audit logs are never manually created

    def has_change_permission(self, request, obj=None):
        return False  # Audit logs are never edited