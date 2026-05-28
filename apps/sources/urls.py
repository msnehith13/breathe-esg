from django.urls import path
from .views import SAPIngestView, UtilityIngestView, TravelIngestView

urlpatterns = [
    path('ingest/sap/', SAPIngestView.as_view(), name='ingest-sap'),
    path('ingest/utility/', UtilityIngestView.as_view(), name='ingest-utility'),
    path('ingest/travel/', TravelIngestView.as_view(), name='ingest-travel'),
]
