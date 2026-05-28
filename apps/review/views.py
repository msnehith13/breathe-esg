from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.ingestion.models import IngestionRun
from apps.emissions.models import NormalizedRecord
from apps.review.models import AnalystFlag, AuditLog
from apps.review.serializers import (
    IngestionRunSerializer,
    NormalizedRecordSerializer,
    RecordEditSerializer,
)


class IngestionRunListView(APIView):
    """
    Lists all ingestion runs for the current user's org.
    Analysts see only their org's data — tenant isolation enforced here.
    """
    def get(self, request):
        runs = IngestionRun.objects.filter(
            org=request.user.org
        ).order_by('-created_at')
        serializer = IngestionRunSerializer(runs, many=True)
        return Response(serializer.data)


class RunRecordListView(APIView):
    """
    Lists all normalized records for a specific ingestion run.
    Supports filter by approval_status and parse_status via query params.
    """
    def get(self, request, run_id):
        try:
            run = IngestionRun.objects.get(id=run_id, org=request.user.org)
        except IngestionRun.DoesNotExist:
            return Response({'error': 'Run not found'}, status=status.HTTP_404_NOT_FOUND)

        records = NormalizedRecord.objects.filter(
            raw_record__ingestion_run=run
        ).select_related('raw_record').prefetch_related('flags')

        # Optional filters
        approval_filter = request.query_params.get('approval_status')
        if approval_filter:
            records = records.filter(approval_status=approval_filter)

        parse_filter = request.query_params.get('parse_status')
        if parse_filter:
            records = records.filter(raw_record__parse_status=parse_filter)

        serializer = NormalizedRecordSerializer(records, many=True)
        return Response({
            'run': IngestionRunSerializer(run).data,
            'records': serializer.data,
        })


class ApproveRunView(APIView):
    """
    Batch-approves all PENDING records in a run.
    Already approved or rejected records are skipped.
    Writes one audit log entry per approved record.
    """
    def post(self, request, run_id):
        try:
            run = IngestionRun.objects.get(id=run_id, org=request.user.org)
        except IngestionRun.DoesNotExist:
            return Response({'error': 'Run not found'}, status=status.HTTP_404_NOT_FOUND)

        pending_records = NormalizedRecord.objects.filter(
            raw_record__ingestion_run=run,
            approval_status=NormalizedRecord.ApprovalStatus.PENDING
        )

        approved_count = 0
        for record in pending_records:
            before_state = {'approval_status': record.approval_status}

            record.approval_status = NormalizedRecord.ApprovalStatus.APPROVED
            record.approved_by = request.user
            record.approved_at = timezone.now()
            record.save(update_fields=['approval_status', 'approved_by', 'approved_at'])

            AuditLog.objects.create(
                org=request.user.org,
                actor=request.user,
                action=AuditLog.Action.APPROVED,
                normalized_record=record,
                ingestion_run=run,
                before_state=before_state,
                after_state={'approval_status': NormalizedRecord.ApprovalStatus.APPROVED}
            )
            approved_count += 1

        return Response({
            'approved_count': approved_count,
            'run_id': run_id,
        })


class FlagRecordView(APIView):
    """
    Analyst raises a flag on a specific normalized record.
    Reason is required. Flags are additive — existing flags are not replaced.
    """
    def post(self, request, record_id):
        try:
            record = NormalizedRecord.objects.get(
                id=record_id,
                org=request.user.org
            )
        except NormalizedRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response({'error': 'Reason is required'}, status=status.HTTP_400_BAD_REQUEST)

        flag = AnalystFlag.objects.create(
            normalized_record=record,
            flagged_by=request.user,
            reason=reason,
        )

        AuditLog.objects.create(
            org=request.user.org,
            actor=request.user,
            action=AuditLog.Action.FLAGGED,
            normalized_record=record,
            before_state=None,
            after_state={'flag_reason': reason}
        )

        return Response({
            'flag_id': flag.id,
            'record_id': record_id,
            'reason': reason,
        }, status=status.HTTP_201_CREATED)


class EditRecordView(APIView):
    """
    Analyst manually edits a normalized record.
    Approved records cannot be edited — immutability after approval.
    Tracks before/after state in audit log.
    """
    def patch(self, request, record_id):
        try:
            record = NormalizedRecord.objects.get(
                id=record_id,
                org=request.user.org
            )
        except NormalizedRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

        if record.approval_status == NormalizedRecord.ApprovalStatus.APPROVED:
            return Response(
                {'error': 'Approved records cannot be edited'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RecordEditSerializer(record, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        before_state = {
            'quantity': str(record.quantity),
            'normalized_quantity': str(record.normalized_quantity),
            'activity_date': str(record.activity_date),
            'description': record.description,
        }

        serializer.save(is_manually_edited=True)

        AuditLog.objects.create(
            org=request.user.org,
            actor=request.user,
            action=AuditLog.Action.EDITED,
            normalized_record=record,
            before_state=before_state,
            after_state=request.data
        )

        return Response(NormalizedRecordSerializer(record).data)

class RecordDetailView(APIView):
    def get(self, request, record_id):
        try:
            record = NormalizedRecord.objects.get(
                id=record_id,
                org=request.user.org
            )
        except NormalizedRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(NormalizedRecordSerializer(record).data)