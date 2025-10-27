from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.utils import APIResponse
from .models import (
    Payment, MpesaTransaction, EscrowAccount,
    PaymentWebhook, PaymentRefund, PaymentAnalytics
)
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, MpesaTransactionSerializer,
    EscrowAccountSerializer, PaymentRefundSerializer, PaymentRefundCreateSerializer,
    PaymentStatusUpdateSerializer, MpesaCallbackSerializer, PaymentAnalyticsSerializer
)
from .services import PaymentProcessingService, MpesaService
import logging

logger = logging.getLogger(__name__)


class PaymentListCreateView(generics.ListCreateAPIView):
    """List user's payments or create new payment"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_method', 'order']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.filter(payer=self.request.user).select_related('order')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    @extend_schema(
        summary="List user payments",
        description="Get list of authenticated user's payments with filtering options",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by payment status'),
            OpenApiParameter('payment_method', OpenApiTypes.STR, description='Filter by payment method'),
            OpenApiParameter('order', OpenApiTypes.UUID, description='Filter by order ID'),
        ],
        responses={200: PaymentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new payment",
        description="Initiate a new payment for an order",
        request=PaymentCreateSerializer,
        responses={
            201: PaymentSerializer,
            400: OpenApiResponse(description="Bad request")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Create payment record
                payment = serializer.save(payer=request.user)

                # Initiate payment processing
                processing_service = PaymentProcessingService()
                phone_number = serializer.validated_data.get('phone_number')

                result = processing_service.initiate_payment(payment, phone_number)

                if result['success']:
                    # Create escrow account for seller protection
                    if payment.order and hasattr(payment.order, 'items'):
                        # Get first seller (could be enhanced for multi-vendor)
                        order_items = payment.order.items.select_related('product__farmer').first()
                        if order_items:
                            processing_service.create_escrow_account(
                                payment, order_items.product.farmer.id
                            )

                    response_data = PaymentSerializer(payment).data
                    response_data.update(result)
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    # Payment initiation failed, delete the payment record
                    payment.delete()
                    return Response({
                        'error': result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment details"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(payer=self.request.user).select_related('order')

    @extend_schema(
        summary="Get payment details",
        description="Retrieve detailed information about a specific payment",
        responses={200: PaymentSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Update payment status",
    description="Update the status of a payment (admin only)",
    request=PaymentStatusUpdateSerializer,
    responses={200: PaymentSerializer}
)
@api_view(['PUT'])
@permission_classes([permissions.IsAdminUser])
def update_payment_status(request, payment_id):
    """Update payment status (admin only)"""
    try:
        payment = Payment.objects.get(payment_id=payment_id)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PaymentStatusUpdateSerializer(
        data=request.data,
        context={'payment': payment}
    )

    if serializer.is_valid():
        payment.status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason')
        if reason:
            payment.failure_reason = reason
        payment.save()

        return Response(PaymentSerializer(payment).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="M-Pesa payment callback",
    description="Handle M-Pesa payment callbacks from Daraja API",
    request=MpesaCallbackSerializer,
    responses={200: OpenApiResponse(description="Callback processed")}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # M-Pesa callbacks don't include auth
def mpesa_callback(request):
    """Handle M-Pesa payment callbacks"""
    try:
        # Validate IP address
        mpesa_service = MpesaService()
        client_ip = request.META.get('REMOTE_ADDR', '')

        if not mpesa_service.validate_callback_ip(client_ip):
            logger.warning(f"Invalid M-Pesa callback IP: {client_ip}")
            return Response({
                'ResultCode': 1,
                'ResultDesc': 'Invalid source IP'
            }, status=status.HTTP_403_FORBIDDEN)

        # Store webhook data
        webhook = PaymentWebhook.objects.create(
            webhook_type='mpesa_callback',
            raw_data=request.data,
            source_ip=client_ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Process callback
        processed_data = mpesa_service.process_callback(request.data)

        if 'checkout_request_id' in processed_data:
            try:
                # Find the corresponding M-Pesa transaction
                mpesa_transaction = MpesaTransaction.objects.get(
                    checkout_request_id=processed_data['checkout_request_id']
                )

                # Update transaction with callback data
                mpesa_transaction.result_code = processed_data.get('result_code')
                mpesa_transaction.result_desc = processed_data.get('result_desc')

                if processed_data['success']:
                    metadata = processed_data.get('metadata', {})
                    mpesa_transaction.mpesa_receipt_number = metadata.get('mpesa_receipt_number')
                    mpesa_transaction.transaction_date = metadata.get('transaction_date')
                    mpesa_transaction.save()

                    # Update payment status
                    payment = mpesa_transaction.payment
                    payment.status = 'completed'
                    payment.payment_date = timezone.now()
                    payment.external_transaction_id = metadata.get('mpesa_receipt_number')
                    payment.save()

                    # Update order payment status
                    if payment.order:
                        payment.order.payment_status = 'paid'
                        payment.order.save()

                    webhook.payment = payment
                    webhook.processed = True
                    webhook.save()

                else:
                    # Payment failed
                    mpesa_transaction.save()
                    payment = mpesa_transaction.payment
                    payment.status = 'failed'
                    payment.failure_reason = processed_data.get('result_desc')
                    payment.save()

                    webhook.payment = payment
                    webhook.processed = True
                    webhook.save()

            except MpesaTransaction.DoesNotExist:
                webhook.processing_error = f"M-Pesa transaction not found for checkout request: {processed_data.get('checkout_request_id')}"
                webhook.save()

        return Response({
            'ResultCode': 0,
            'ResultDesc': 'Accepted'
        })

    except Exception as e:
        logger.error(f"Error processing M-Pesa callback: {e}")
        return Response({
            'ResultCode': 1,
            'ResultDesc': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Query M-Pesa payment status",
    description="Check the status of an M-Pesa payment",
    responses={200: MpesaTransactionSerializer}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def query_mpesa_payment(request, payment_id):
    """Query M-Pesa payment status"""
    try:
        payment = Payment.objects.get(payment_id=payment_id, payer=request.user)
        mpesa_transaction = payment.mpesa_transaction

        mpesa_service = MpesaService()
        result = mpesa_service.query_stk_status(mpesa_transaction.checkout_request_id)

        if result['success']:
            # Update transaction with latest status
            data = result['data']
            mpesa_transaction.result_code = data.get('ResultCode')
            mpesa_transaction.result_desc = data.get('ResultDesc')
            mpesa_transaction.save()

            return Response(MpesaTransactionSerializer(mpesa_transaction).data)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except AttributeError:
        return Response({
            'error': 'M-Pesa transaction not found for this payment'
        }, status=status.HTTP_404_NOT_FOUND)


class PaymentRefundListCreateView(generics.ListCreateAPIView):
    """List user's refund requests or create new refund"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment']
    ordering = ['-created_at']

    def get_queryset(self):
        return PaymentRefund.objects.filter(
            payment__payer=self.request.user
        ).select_related('payment')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentRefundCreateSerializer
        return PaymentRefundSerializer

    @extend_schema(
        summary="Request payment refund",
        description="Request a refund for a completed payment",
        request=PaymentRefundCreateSerializer,
        responses={201: PaymentRefundSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            refund = serializer.save()
            return Response(
                PaymentRefundSerializer(refund).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Release escrow funds",
    description="Release funds from escrow to seller (buyer or admin only)",
    responses={200: EscrowAccountSerializer}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def release_escrow_funds(request, escrow_id):
    """Release escrow funds"""
    try:
        escrow = EscrowAccount.objects.get(id=escrow_id)

        # Check permissions (buyer or admin can release)
        if not (request.user == escrow.payment.payer or request.user.is_staff):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)

        processing_service = PaymentProcessingService()
        result = processing_service.release_escrow_funds(
            str(escrow_id),
            release_reason='Released by buyer'
        )

        if result['success']:
            escrow.refresh_from_db()
            return Response(EscrowAccountSerializer(escrow).data)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

    except EscrowAccount.DoesNotExist:
        return Response({
            'error': 'Escrow account not found'
        }, status=status.HTTP_404_NOT_FOUND)


class PaymentAnalyticsView(generics.ListAPIView):
    """Payment analytics for admin users"""
    serializer_class = PaymentAnalyticsSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']
    ordering = ['-date']

    def get_queryset(self):
        return PaymentAnalytics.objects.all()

    @extend_schema(
        summary="Get payment analytics",
        description="Retrieve payment analytics data (admin only)",
        responses={200: PaymentAnalyticsSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
