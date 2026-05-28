from django.db import models

# Create your models here.
from django.db import models
from apps.organizations.models import Organization, User
from apps.emissions.models import NormalizedRecord
from apps.ingestion.models import IngestionRun


class AnalystFlag(models.Model):
    """
    Analyst-raised flag on a specific normalized record.
    Separate model because one record can accumulate multiple flags
    across its review lifecycle.
    """
    normalized_record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    flagged_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='flags_raised')
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='flags_resolved'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Flag on record {self.normalized_record_id} | resolved={self.resolved}"


class AuditLog(models.Model):
    """
    Immutable record of every meaningful state change.
    Written at the service layer — never updated, never deleted.
    before_state and after_state are JSON snapshots for full traceability.
    """

    class Action(models.TextChoices):
        INGESTED = 'INGESTED', 'Data Ingested'
        FLAGGED = 'FLAGGED', 'Record Flagged'
        EDITED = 'EDITED', 'Record Manually Edited'
        APPROVED = 'APPROVED', 'Record Approved'
        REJECTED = 'REJECTED', 'Record Rejected'
        FLAG_RESOLVED = 'FLAG_RESOLVED', 'Flag Resolved'

    org = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='audit_logs')
    actor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)

    # One of these will be set depending on what the action applies to
    normalized_record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    ingestion_run = models.ForeignKey(
        IngestionRun,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"