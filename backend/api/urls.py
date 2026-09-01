from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/me/', views.me_view, name='me'),
    path('upload/orders/', views.upload_orders, name='upload_orders'),
    path('upload/payments/', views.upload_payments, name='upload_payments'),
    path('reconcile/', views.run_reconciliation, name='reconcile'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),
    path('discrepancies/', views.discrepancy_list, name='discrepancy_list'),
    path('explain/', views.explain_discrepancies, name='explain_discrepancies'),
]
