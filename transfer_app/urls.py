from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.TransferView.as_view(), name='get_all_files'),
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('revoke/', views.RevokeView.as_view(), name='revoke'),
    path('transfer/history/', views.TransferHistoryView.as_view(), name='transfer_history'),
]