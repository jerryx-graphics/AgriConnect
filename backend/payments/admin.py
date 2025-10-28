from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Payment, MpesaTransaction, EscrowAccount,
    PaymentWebhook, PaymentRefund, PaymentAnalytics
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'order', 'payer', 'amount', 'currency',
        'payment_method', 'status', 'payment_date', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['payment_id', 'order__order_id', 'payer__email', 'external_transaction_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    raw_id_fields = ['order', 'payer']

    fieldsets = (
        ('Basic Information', {
            'fields': ('payment_id', 'order', 'payer', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'description', 'payment_date')
        }),
        ('External References', {
            'fields': ('external_transaction_id', 'gateway_response')
        }),
        ('Error Handling', {
            'fields': ('failure_reason',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'payer')


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'phone_number', 'mpesa_receipt_number',
        'transaction_type', 'result_code', 'transaction_date'
    ]
    list_filter = ['transaction_type', 'result_code', 'transaction_date']
    search_fields = [
        'phone_number', 'mpesa_receipt_number', 'checkout_request_id',
        'merchant_request_id', 'account_reference'
    ]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['payment']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('payment', 'phone_number', 'transaction_type', 'mpesa_receipt_number')
        }),
        ('Daraja API Fields', {
            'fields': ('checkout_request_id', 'merchant_request_id', 'result_code', 'result_desc')
        }),
        ('M-Pesa Details', {
            'fields': ('transaction_date', 'account_reference', 'transaction_desc')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'seller', 'amount', 'status',
        'auto_release_days', 'release_date', 'created_at'
    ]
    list_filter = ['status', 'auto_release_days', 'created_at']
    search_fields = ['payment__payment_id', 'seller__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['payment', 'seller']

    fieldsets = (
        ('Escrow Details', {
            'fields': ('payment', 'seller', 'amount', 'status')
        }),
        ('Release Conditions', {
            'fields': ('auto_release_days', 'release_date')
        }),
        ('Dispute Management', {
            'fields': ('dispute_reason', 'dispute_date', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'webhook_type', 'payment', 'processed', 'created_at', 'source_ip'
    ]
    list_filter = ['webhook_type', 'processed', 'created_at']
    search_fields = ['payment__payment_id', 'source_ip']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['payment']

    fieldsets = (
        ('Webhook Information', {
            'fields': ('webhook_type', 'payment', 'processed')
        }),
        ('Request Details', {
            'fields': ('source_ip', 'user_agent')
        }),
        ('Data', {
            'fields': ('raw_data', 'processing_error')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'amount', 'status', 'processed_by', 'processed_at', 'created_at'
    ]
    list_filter = ['status', 'processed_at', 'created_at']
    search_fields = ['payment__payment_id', 'refund_reference', 'external_refund_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['payment', 'processed_by']

    fieldsets = (
        ('Refund Details', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_at', 'refund_reference')
        }),
        ('External References', {
            'fields': ('external_refund_id', 'gateway_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PaymentAnalytics)
class PaymentAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_transactions', 'successful_transactions',
        'total_amount', 'amount_in_escrow'
    ]
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Transaction Metrics', {
            'fields': ('total_transactions', 'successful_transactions', 'failed_transactions')
        }),
        ('Amount Metrics', {
            'fields': ('total_amount', 'total_fees_collected')
        }),
        ('M-Pesa Metrics', {
            'fields': ('mpesa_transactions', 'mpesa_amount')
        }),
        ('Escrow Metrics', {
            'fields': ('amount_in_escrow', 'escrow_releases')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
