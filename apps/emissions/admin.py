from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import NormalizedRecord


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'org', 'source_type', 'scope', 'category', 'activity_date', 'normalized_quantity', 'normalized_unit', 'approval_status']
    list_filter = ['source_type', 'scope', 'approval_status', 'org']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']