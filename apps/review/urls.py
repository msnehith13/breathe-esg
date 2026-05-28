from django.urls import path
from .views import (
    IngestionRunListView,
    RunRecordListView,
    ApproveRunView,
    FlagRecordView,
    EditRecordView,
)

urlpatterns = [
    path('runs/', IngestionRunListView.as_view(), name='run-list'),
    path('runs/<int:run_id>/records/', RunRecordListView.as_view(), name='run-records'),
    path('runs/<int:run_id>/approve/', ApproveRunView.as_view(), name='run-approve'),
    path('records/<int:record_id>/flag/', FlagRecordView.as_view(), name='record-flag'),
    path('records/<int:record_id>/edit/', EditRecordView.as_view(), name='record-edit'),
]

from .views import (
    IngestionRunListView,
    RunRecordListView,
    ApproveRunView,
    FlagRecordView,
    EditRecordView,
    RecordDetailView,
)

urlpatterns = [
    path('runs/', IngestionRunListView.as_view(), name='run-list'),
    path('runs/<int:run_id>/records/', RunRecordListView.as_view(), name='run-records'),
    path('runs/<int:run_id>/approve/', ApproveRunView.as_view(), name='run-approve'),
    path('records/<int:record_id>/', RecordDetailView.as_view(), name='record-detail'),
    path('records/<int:record_id>/flag/', FlagRecordView.as_view(), name='record-flag'),
    path('records/<int:record_id>/edit/', EditRecordView.as_view(), name='record-edit'),
]