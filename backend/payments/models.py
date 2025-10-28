from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from core.models import BaseModel
from core.utils import generate_transaction_id

User = get_user_model()


class Payment(BaseModel):
    """Main payment record for orders"""
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    payment_id = models.CharField(max_length=20, unique=True, default=generate_transaction_id)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')

    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mpesa')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # External payment references
    external_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    # Metadata
    description = models.TextField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"


class MpesaTransaction(BaseModel):
    """M-Pesa specific transaction details"""
    TRANSACTION_TYPE_CHOICES = [
        ('paybill', 'Pay Bill'),
        ('till', 'Buy Goods Till'),
        ('c2b', 'Customer to Business'),
        ('b2c', 'Business to Customer'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mpesa_transaction')
    phone_number = models.CharField(max_length=15)
    mpesa_receipt_number = models.CharField(max_length=20, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='paybill')

    # Daraja API specific fields
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)

    # Transaction details from M-Pesa
    transaction_date = models.DateTimeField(null=True, blank=True)
    account_reference = models.CharField(max_length=50, null=True, blank=True)
    transaction_desc = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'payments_mpesa_transaction'

    def __str__(self):
        return f"M-Pesa {self.phone_number} - {self.mpesa_receipt_number}"


class EscrowAccount(BaseModel):
    """Escrow account for secure payments"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('held', 'Held'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='escrow')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_accounts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Release conditions
    release_date = models.DateTimeField(null=True, blank=True)
    auto_release_days = models.IntegerField(default=7)  # Auto-release after 7 days

    # Dispute handling
    dispute_reason = models.TextField(null=True, blank=True)
    dispute_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'payments_escrow_account'

    def __str__(self):
        return f"Escrow {self.payment.payment_id} - {self.amount} KES"


class PaymentWebhook(BaseModel):
    """Store webhook data from payment gateways"""
    WEBHOOK_TYPE_CHOICES = [
        ('mpesa_callback', 'M-Pesa Callback'),
        ('mpesa_result', 'M-Pesa Result'),
        ('bank_notification', 'Bank Notification'),
    ]

    webhook_type = models.CharField(max_length=50, choices=WEBHOOK_TYPE_CHOICES)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhooks')

    # Raw webhook data
    raw_data = models.JSONField()
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)

    # Request metadata
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'payments_webhook'
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.webhook_type} - {self.created_at}"


class PaymentRefund(BaseModel):
    """Refund records for payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Refund processing
    refund_reference = models.CharField(max_length=100, null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_refunds')
    processed_at = models.DateTimeField(null=True, blank=True)

    # External refund details
    external_refund_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'payments_refund'

    def __str__(self):
        return f"Refund {self.payment.payment_id} - {self.amount} KES"


class PaymentAnalytics(BaseModel):
    """Track payment analytics and metrics"""
    date = models.DateField()

    # Transaction counts
    total_transactions = models.IntegerField(default=0)
    successful_transactions = models.IntegerField(default=0)
    failed_transactions = models.IntegerField(default=0)

    # Amount metrics
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fees_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Payment method breakdown
    mpesa_transactions = models.IntegerField(default=0)
    mpesa_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Escrow metrics
    amount_in_escrow = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    escrow_releases = models.IntegerField(default=0)

    class Meta:
        db_table = 'payments_analytics'
        unique_together = ['date']

    def __str__(self):
        return f"Payment Analytics {self.date}"
