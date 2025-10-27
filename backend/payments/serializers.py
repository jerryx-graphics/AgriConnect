from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Payment, MpesaTransaction, EscrowAccount,
    PaymentWebhook, PaymentRefund, PaymentAnalytics
)

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer for API responses"""

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'order', 'payer', 'amount', 'currency',
            'payment_method', 'status', 'description', 'payment_date',
            'external_transaction_id', 'failure_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'payment_id', 'payer', 'external_transaction_id',
            'payment_date', 'failure_reason', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add related order information
        if instance.order:
            data['order_details'] = {
                'order_id': instance.order.order_id,
                'total_amount': instance.order.total_amount,
                'status': instance.order.status
            }
        return data


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    phone_number = serializers.CharField(max_length=15, required=False, write_only=True)

    class Meta:
        model = Payment
        fields = [
            'order', 'amount', 'payment_method', 'description', 'phone_number'
        ]

    def validate_phone_number(self, value):
        """Validate phone number for M-Pesa payments"""
        if value:
            # Basic Kenyan phone number validation
            import re
            pattern = r'^(\+254|254|0)?[17]\d{8}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError(
                    "Invalid Kenyan phone number format"
                )
        return value

    def validate(self, attrs):
        """Validate payment data"""
        payment_method = attrs.get('payment_method')
        phone_number = attrs.get('phone_number')

        # M-Pesa requires phone number
        if payment_method == 'mpesa' and not phone_number:
            raise serializers.ValidationError({
                'phone_number': 'Phone number is required for M-Pesa payments'
            })

        # Validate order exists and belongs to user
        order = attrs.get('order')
        if order and order.buyer != self.context['request'].user:
            raise serializers.ValidationError({
                'order': 'You can only make payments for your own orders'
            })

        return attrs


class MpesaTransactionSerializer(serializers.ModelSerializer):
    """M-Pesa transaction serializer"""

    class Meta:
        model = MpesaTransaction
        fields = [
            'id', 'payment', 'phone_number', 'mpesa_receipt_number',
            'transaction_type', 'checkout_request_id', 'merchant_request_id',
            'result_code', 'result_desc', 'transaction_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'payment', 'mpesa_receipt_number', 'checkout_request_id',
            'merchant_request_id', 'result_code', 'result_desc',
            'transaction_date', 'created_at'
        ]


class EscrowAccountSerializer(serializers.ModelSerializer):
    """Escrow account serializer"""

    class Meta:
        model = EscrowAccount
        fields = [
            'id', 'payment', 'seller', 'amount', 'status',
            'release_date', 'auto_release_days', 'dispute_reason',
            'dispute_date', 'resolution_notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'payment', 'seller', 'amount', 'release_date',
            'dispute_date', 'created_at'
        ]


class PaymentRefundSerializer(serializers.ModelSerializer):
    """Payment refund serializer"""

    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'amount', 'reason', 'status',
            'refund_reference', 'processed_by', 'processed_at',
            'external_refund_id', 'created_at'
        ]
        read_only_fields = [
            'id', 'payment', 'status', 'refund_reference',
            'processed_by', 'processed_at', 'external_refund_id',
            'created_at'
        ]


class PaymentRefundCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating refund requests"""

    class Meta:
        model = PaymentRefund
        fields = ['payment', 'amount', 'reason']

    def validate_payment(self, value):
        """Validate payment can be refunded"""
        if value.status not in ['completed', 'paid']:
            raise serializers.ValidationError(
                "Only completed payments can be refunded"
            )
        return value

    def validate_amount(self, value):
        """Validate refund amount"""
        if value <= 0:
            raise serializers.ValidationError(
                "Refund amount must be greater than zero"
            )
        return value

    def validate(self, attrs):
        """Validate refund request"""
        payment = attrs.get('payment')
        amount = attrs.get('amount')

        if payment and amount > payment.amount:
            raise serializers.ValidationError({
                'amount': 'Refund amount cannot exceed payment amount'
            })

        # Check for existing refunds
        existing_refunds = PaymentRefund.objects.filter(
            payment=payment,
            status__in=['pending', 'processing', 'completed']
        ).aggregate(total=serializers.Sum('amount'))['total'] or 0

        if existing_refunds + amount > payment.amount:
            raise serializers.ValidationError({
                'amount': 'Total refunds cannot exceed payment amount'
            })

        return attrs


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Payment webhook serializer"""

    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'webhook_type', 'payment', 'raw_data', 'processed',
            'processing_error', 'source_ip', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentAnalyticsSerializer(serializers.ModelSerializer):
    """Payment analytics serializer"""

    class Meta:
        model = PaymentAnalytics
        fields = [
            'id', 'date', 'total_transactions', 'successful_transactions',
            'failed_transactions', 'total_amount', 'total_fees_collected',
            'mpesa_transactions', 'mpesa_amount', 'amount_in_escrow',
            'escrow_releases', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating payment status"""
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)
    reason = serializers.CharField(max_length=500, required=False)

    def validate_status(self, value):
        """Validate status transition"""
        payment = self.context.get('payment')
        if not payment:
            return value

        # Define allowed status transitions
        allowed_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'failed', 'cancelled'],
            'completed': ['refunded'],
            'failed': ['pending'],  # Allow retry
            'cancelled': [],  # No transitions from cancelled
            'refunded': []  # No transitions from refunded
        }

        current_status = payment.status
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )

        return value


class MpesaCallbackSerializer(serializers.Serializer):
    """Serializer for processing M-Pesa callbacks"""
    Body = serializers.DictField()

    def validate_Body(self, value):
        """Validate M-Pesa callback structure"""
        stk_callback = value.get('stkCallback')
        if not stk_callback:
            raise serializers.ValidationError("Invalid callback structure")

        required_fields = ['MerchantRequestID', 'CheckoutRequestID', 'ResultCode']
        for field in required_fields:
            if field not in stk_callback:
                raise serializers.ValidationError(f"Missing required field: {field}")

        return value