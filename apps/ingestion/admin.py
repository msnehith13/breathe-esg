from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import IngestionRun, RawRecord


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'org', 'source_type', 'file_name', 'status', 'row_count', 'failed_count', 'flagged_count', 'created_at']
    list_filter = ['source_type', 'status', 'org']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingestion_run', 'row_number', 'parse_status', 'created_at']
    list_filter = ['parse_status']
    readonly_fields = ['created_at']