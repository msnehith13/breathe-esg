from rest_framework import serializers
from apps.ingestion.models import IngestionRun, RawRecord
from apps.emissions.models import NormalizedRecord
from apps.review.models import AnalystFlag, AuditLog


class IngestionRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionRun
        fields = [
            'id', 'source_type', 'file_name', 'status',
            'row_count', 'failed_count', 'flagged_count',
            'created_at', 'completed_at'
        ]


class AnalystFlagSerializer(serializers.ModelSerializer):
    flagged_by_username = serializers.CharField(source='flagged_by.username', read_only=True)

    class Meta:
        model = AnalystFlag
        fields = ['id', 'reason', 'resolved', 'flagged_by_username', 'created_at']


class NormalizedRecordSerializer(serializers.ModelSerializer):
    flags = AnalystFlagSerializer(many=True, read_only=True)
    raw_parse_status = serializers.CharField(source='raw_record.parse_status', read_only=True)
    raw_parse_errors = serializers.JSONField(source='raw_record.parse_errors', read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'source_type', 'scope', 'category',
            'activity_date', 'quantity', 'original_unit',
            'normalized_quantity', 'normalized_unit',
            'supplier_vendor', 'location', 'description',
            'is_manually_edited', 'edit_notes',
            'approval_status', 'approved_at',
            'raw_parse_status', 'raw_parse_errors',
            'flags', 'created_at', 'updated_at'
        ]


class RecordEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedRecord
        fields = ['quantity', 'normalized_quantity', 'activity_date', 'description', 'edit_notes']