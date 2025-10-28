from django.urls import path
from . import views

urlpatterns = [
    # Payment Management
    path('', views.PaymentListCreateView.as_view(), name='payment-list-create'),
    path('<str:payment_id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<str:payment_id>/status/', views.update_payment_status, name='update-payment-status'),

    # M-Pesa Integration
    path('mpesa/callback/', views.mpesa_callback, name='mpesa-callback'),
    path('<str:payment_id>/mpesa/query/', views.query_mpesa_payment, name='query-mpesa-payment'),

    # Refunds
    path('refunds/', views.PaymentRefundListCreateView.as_view(), name='payment-refund-list-create'),

    # Escrow Management
    path('escrow/<uuid:escrow_id>/release/', views.release_escrow_funds, name='release-escrow-funds'),

    # Analytics (Admin only)
    path('analytics/', views.PaymentAnalyticsView.as_view(), name='payment-analytics'),
]