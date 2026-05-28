from django.db import models

# Create your models here.
from django.db import models
from apps.organizations.models import Organization, User


class IngestionRun(models.Model):
    """
    Represents one upload event — one file or one API pull.
    Every raw record traces back to exactly one ingestion run.
    """

    class SourceType(models.TextChoices):
        SAP = 'SAP', 'SAP Export'
        UTILITY = 'UTILITY', 'Utility Electricity'
        TRAVEL = 'TRAVEL', 'Corporate Travel'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    org = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='ingestion_runs')
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ingestion_runs')
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Summary counts — populated after processing completes
    row_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    flagged_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.source_type} | {self.file_name} | {self.status}"


class RawRecord(models.Model):
    """
    One row from the original file, stored exactly as received.
    Never modified after creation — this is the permanent source-of-truth anchor.
    If normalization has a bug, we re-run against these without re-uploading.
    """

    class ParseStatus(models.TextChoices):
        OK = 'OK', 'Parsed Successfully'
        FAILED = 'FAILED', 'Parse Failed'
        FLAGGED = 'FLAGGED', 'Flagged for Review'

    ingestion_run = models.ForeignKey(IngestionRun, on_delete=models.CASCADE, related_name='raw_records')
    row_number = models.IntegerField()
    raw_data = models.JSONField()  # Original row, untouched
    parse_status = models.CharField(max_length=20, choices=ParseStatus.choices, default=ParseStatus.OK)
    parse_errors = models.JSONField(default=list, blank=True)  # List of error strings

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['row_number']

    def __str__(self):
        return f"Row {self.row_number} | {self.ingestion_run} | {self.parse_status}"