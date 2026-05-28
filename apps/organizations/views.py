from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from apps.ingestion.models import IngestionRun
from apps.review.models import AuditLog
from apps.sources.sap_service import run_sap_ingestion
from apps.sources.utility_service import run_utility_ingestion
from apps.sources.travel_service import run_travel_ingestion


class SAPIngestView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.org:
            return Response({'error': 'User has no organization assigned'}, status=status.HTTP_403_FORBIDDEN)

        ingestion_run = IngestionRun.objects.create(
            org=request.user.org,
            source_type=IngestionRun.SourceType.SAP,
            uploaded_by=request.user,
            file_name=file.name,
            status=IngestionRun.Status.PENDING,
        )
        ingestion_run = run_sap_ingestion(ingestion_run, file.read())

        AuditLog.objects.create(
            org=request.user.org,
            actor=request.user,
            action=AuditLog.Action.INGESTED,
            ingestion_run=ingestion_run,
            before_state=None,
            after_state={
                'source_type': 'SAP',
                'file_name': file.name,
                'row_count': ingestion_run.row_count,
                'failed_count': ingestion_run.failed_count,
                'flagged_count': ingestion_run.flagged_count,
            }
        )

        return Response({
            'ingestion_run_id': ingestion_run.id,
            'status': ingestion_run.status,
            'row_count': ingestion_run.row_count,
            'failed_count': ingestion_run.failed_count,
            'flagged_count': ingestion_run.flagged_count,
        }, status=status.HTTP_201_CREATED)


class UtilityIngestView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.org:
            return Response({'error': 'User has no organization assigned'}, status=status.HTTP_403_FORBIDDEN)

        ingestion_run = IngestionRun.objects.create(
            org=request.user.org,
            source_type=IngestionRun.SourceType.UTILITY,
            uploaded_by=request.user,
            file_name=file.name,
            status=IngestionRun.Status.PENDING,
        )
        ingestion_run = run_utility_ingestion(ingestion_run, file.read())

        AuditLog.objects.create(
            org=request.user.org,
            actor=request.user,
            action=AuditLog.Action.INGESTED,
            ingestion_run=ingestion_run,
            before_state=None,
            after_state={
                'source_type': 'UTILITY',
                'file_name': file.name,
                'row_count': ingestion_run.row_count,
                'failed_count': ingestion_run.failed_count,
                'flagged_count': ingestion_run.flagged_count,
            }
        )

        return Response({
            'ingestion_run_id': ingestion_run.id,
            'status': ingestion_run.status,
            'row_count': ingestion_run.row_count,
            'failed_count': ingestion_run.failed_count,
            'flagged_count': ingestion_run.flagged_count,
        }, status=status.HTTP_201_CREATED)


class TravelIngestView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.endswith('.json'):
            return Response({'error': 'File must be a JSON'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.org:
            return Response({'error': 'User has no organization assigned'}, status=status.HTTP_403_FORBIDDEN)

        ingestion_run = IngestionRun.objects.create(
            org=request.user.org,
            source_type=IngestionRun.SourceType.TRAVEL,
            uploaded_by=request.user,
            file_name=file.name,
            status=IngestionRun.Status.PENDING,
        )
        ingestion_run = run_travel_ingestion(ingestion_run, file.read())

        AuditLog.objects.create(
            org=request.user.org,
            actor=request.user,
            action=AuditLog.Action.INGESTED,
            ingestion_run=ingestion_run,
            before_state=None,
            after_state={
                'source_type': 'TRAVEL',
                'file_name': file.name,
                'row_count': ingestion_run.row_count,
                'failed_count': ingestion_run.failed_count,
                'flagged_count': ingestion_run.flagged_count,
            }
        )

        return Response({
            'ingestion_run_id': ingestion_run.id,
            'status': ingestion_run.status,
            'row_count': ingestion_run.row_count,
            'failed_count': ingestion_run.failed_count,
            'flagged_count': ingestion_run.flagged_count,
        }, status=status.HTTP_201_CREATED)