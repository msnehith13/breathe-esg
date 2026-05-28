from django.db import models

# Create your models here.
from django.db import models
from apps.organizations.models import Organization, User
from apps.ingestion.models import RawRecord


class NormalizedRecord(models.Model):
    """
    The clean, unified output of the ingestion pipeline.
    One record per successfully parsed raw row.
    Links back to its raw origin — never orphaned.
    """

    class SourceType(models.TextChoices):
        SAP = 'SAP', 'SAP Export'
        UTILITY = 'UTILITY', 'Utility Electricity'
        TRAVEL = 'TRAVEL', 'Corporate Travel'

    class Scope(models.TextChoices):
        SCOPE_1 = 'SCOPE_1', 'Scope 1 - Direct Emissions'
        SCOPE_2 = 'SCOPE_2', 'Scope 2 - Purchased Electricity'
        SCOPE_3 = 'SCOPE_3', 'Scope 3 - Value Chain'

    class ApprovalStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    # Tenant + origin
    org = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='normalized_records')
    raw_record = models.OneToOneField(RawRecord, on_delete=models.PROTECT, related_name='normalized')

    # Classification
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    scope = models.CharField(max_length=10, choices=Scope.choices)

    # Category is free text intentionally — GHG Protocol sub-categories vary
    # Examples: "Stationary Combustion", "Purchased Electricity", "Business Travel - Flight"
    category = models.CharField(max_length=255)

    # Activity data
    activity_date = models.DateField()
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    original_unit = models.CharField(max_length=50)  # Exactly what the source said

    # Normalized values — we standardize to a canonical unit per category
    normalized_unit = models.CharField(max_length=50)
    normalized_quantity = models.DecimalField(max_digits=15, decimal_places=4)

    # Optional context fields — populated where source provides them
    supplier_vendor = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)  # Plant code, meter ID, airport pair
    description = models.TextField(blank=True)

    # Edit tracking
    is_manually_edited = models.BooleanField(default=False)
    edit_notes = models.TextField(blank=True)

    # Approval workflow
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_records'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-activity_date']

    def __str__(self):
        return f"{self.source_type} | {self.scope} | {self.activity_date} | {self.normalized_quantity} {self.normalized_unit}"