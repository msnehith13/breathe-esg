from django.utils import timezone
from apps.ingestion.models import IngestionRun, RawRecord
from apps.emissions.models import NormalizedRecord
from apps.sources.utility_parser import parse_utility_file


def run_utility_ingestion(ingestion_run: IngestionRun, file_content: bytes) -> IngestionRun:
    """
    Orchestrates the full utility electricity ingestion pipeline.
    Structure mirrors SAP service intentionally — consistent pattern
    across all three source types.
    """
    ingestion_run.status = IngestionRun.Status.PROCESSING
    ingestion_run.save(update_fields=['status'])

    try:
        parsed_rows = parse_utility_file(file_content)
    except Exception as e:
        ingestion_run.status = IngestionRun.Status.FAILED
        ingestion_run.completed_at = timezone.now()
        ingestion_run.save(update_fields=['status', 'completed_at'])
        raise

    row_count = 0
    failed_count = 0
    flagged_count = 0

    for row_result in parsed_rows:
        row_count += 1
        status = row_result['status']

        parse_status_map = {
            'OK': RawRecord.ParseStatus.OK,
            'FAILED': RawRecord.ParseStatus.FAILED,
            'FLAGGED': RawRecord.ParseStatus.FLAGGED,
        }

        raw_record = RawRecord.objects.create(
            ingestion_run=ingestion_run,
            row_number=row_result['row_number'],
            raw_data=row_result['data'],
            parse_status=parse_status_map[status],
            parse_errors=row_result['errors'],
        )

        if status == 'FAILED':
            failed_count += 1
            continue

        if status == 'FLAGGED':
            flagged_count += 1

        p = row_result['parsed']

        NormalizedRecord.objects.create(
            org=ingestion_run.org,
            raw_record=raw_record,
            source_type=NormalizedRecord.SourceType.UTILITY,
            scope=p['scope'],
            category=p['category'],
            activity_date=p['activity_date'],
            quantity=p['quantity'],
            original_unit=p['original_unit'],
            normalized_unit=p['normalized_unit'],
            normalized_quantity=p['normalized_quantity'],
            supplier_vendor=p.get('supplier_vendor', ''),
            location=p.get('location', ''),
            description=f"Meter {p.get('meter_id', '')} — {p.get('site_name', '')}",
            approval_status=NormalizedRecord.ApprovalStatus.PENDING,
        )

    ingestion_run.status = IngestionRun.Status.COMPLETED
    ingestion_run.row_count = row_count
    ingestion_run.failed_count = failed_count
    ingestion_run.flagged_count = flagged_count
    ingestion_run.completed_at = timezone.now()
    ingestion_run.save(update_fields=[
        'status', 'row_count', 'failed_count', 'flagged_count', 'completed_at'
    ])

    return ingestion_run