from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import (
    Payment, EscrowAccount, PaymentAnalytics,
    PaymentWebhook, MpesaTransaction
)
from .services import PaymentProcessingService, MpesaService
import logging

logger = logging.getLogger(__name__)


@shared_task
def auto_release_escrow_funds():
    """
    Automatically release escrow funds after the auto-release period
    Runs daily to check for eligible escrow accounts
    """
    try:
        now = timezone.now()

        # Find escrow accounts eligible for auto-release
        eligible_escrows = EscrowAccount.objects.filter(
            status='active',
            created_at__lte=now - timedelta(days=7)  # Default 7 days
        ).select_related('payment', 'seller')

        released_count = 0
        processing_service = PaymentProcessingService()

        for escrow in eligible_escrows:
            # Check if enough days have passed
            days_held = (now - escrow.created_at).days
            if days_held >= escrow.auto_release_days:

                # Verify payment is still completed
                if escrow.payment.status == 'completed':
                    result = processing_service.release_escrow_funds(
                        str(escrow.id),
                        release_reason='Auto-released after {} days'.format(days_held)
                    )

                    if result['success']:
                        released_count += 1
                        logger.info(f"Auto-released escrow {escrow.id} after {days_held} days")
                    else:
                        logger.error(f"Failed to auto-release escrow {escrow.id}: {result['message']}")

        logger.info(f"Auto-release task completed. Released {released_count} escrow accounts.")
        return {'released_count': released_count}

    except Exception as e:
        logger.error(f"Error in auto_release_escrow_funds task: {e}")
        return {'error': str(e)}


@shared_task
def generate_daily_payment_analytics():
    """
    Generate daily payment analytics
    Runs daily to aggregate payment data
    """
    try:
        yesterday = timezone.now().date() - timedelta(days=1)

        # Check if analytics already exist for yesterday
        analytics, created = PaymentAnalytics.objects.get_or_create(
            date=yesterday,
            defaults={
                'total_transactions': 0,
                'successful_transactions': 0,
                'failed_transactions': 0,
                'total_amount': 0,
                'total_fees_collected': 0,
                'mpesa_transactions': 0,
                'mpesa_amount': 0,
                'amount_in_escrow': 0,
                'escrow_releases': 0,
            }
        )

        if not created:
            logger.info(f"Analytics for {yesterday} already exist, updating...")

        # Calculate payment metrics for yesterday
        yesterday_payments = Payment.objects.filter(
            created_at__date=yesterday
        )

        analytics.total_transactions = yesterday_payments.count()
        analytics.successful_transactions = yesterday_payments.filter(
            status__in=['completed', 'paid']
        ).count()
        analytics.failed_transactions = yesterday_payments.filter(
            status='failed'
        ).count()

        # Calculate amounts
        completed_payments = yesterday_payments.filter(status__in=['completed', 'paid'])
        analytics.total_amount = completed_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Calculate platform fees (3% default)
        analytics.total_fees_collected = analytics.total_amount * 0.03

        # M-Pesa specific metrics
        mpesa_payments = completed_payments.filter(payment_method='mpesa')
        analytics.mpesa_transactions = mpesa_payments.count()
        analytics.mpesa_amount = mpesa_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Escrow metrics
        analytics.amount_in_escrow = EscrowAccount.objects.filter(
            status='active',
            created_at__date=yesterday
        ).aggregate(total=Sum('amount'))['total'] or 0

        analytics.escrow_releases = EscrowAccount.objects.filter(
            status='released',
            release_date__date=yesterday
        ).count()

        analytics.save()

        logger.info(f"Generated analytics for {yesterday}: {analytics.total_transactions} transactions")
        return {
            'date': str(yesterday),
            'total_transactions': analytics.total_transactions,
            'total_amount': float(analytics.total_amount)
        }

    except Exception as e:
        logger.error(f"Error generating daily analytics: {e}")
        return {'error': str(e)}


@shared_task
def process_pending_webhooks():
    """
    Process pending payment webhooks
    Runs periodically to handle failed webhook processing
    """
    try:
        pending_webhooks = PaymentWebhook.objects.filter(
            processed=False,
            processing_error__isnull=True,
            created_at__gte=timezone.now() - timedelta(hours=24)  # Only last 24 hours
        )

        processed_count = 0
        mpesa_service = MpesaService()

        for webhook in pending_webhooks:
            try:
                if webhook.webhook_type == 'mpesa_callback':
                    # Reprocess M-Pesa callback
                    processed_data = mpesa_service.process_callback(webhook.raw_data)

                    if 'checkout_request_id' in processed_data:
                        mpesa_transaction = MpesaTransaction.objects.filter(
                            checkout_request_id=processed_data['checkout_request_id']
                        ).first()

                        if mpesa_transaction:
                            # Update transaction and payment status
                            mpesa_transaction.result_code = processed_data.get('result_code')
                            mpesa_transaction.result_desc = processed_data.get('result_desc')

                            if processed_data['success']:
                                metadata = processed_data.get('metadata', {})
                                mpesa_transaction.mpesa_receipt_number = metadata.get('mpesa_receipt_number')
                                mpesa_transaction.transaction_date = metadata.get('transaction_date')
                                mpesa_transaction.save()

                                payment = mpesa_transaction.payment
                                payment.status = 'completed'
                                payment.payment_date = timezone.now()
                                payment.external_transaction_id = metadata.get('mpesa_receipt_number')
                                payment.save()

                                if payment.order:
                                    payment.order.payment_status = 'paid'
                                    payment.order.save()

                            webhook.payment = mpesa_transaction.payment
                            webhook.processed = True
                            webhook.save()
                            processed_count += 1
                        else:
                            webhook.processing_error = "M-Pesa transaction not found"
                            webhook.save()

            except Exception as e:
                webhook.processing_error = str(e)
                webhook.save()
                logger.error(f"Error processing webhook {webhook.id}: {e}")

        logger.info(f"Processed {processed_count} pending webhooks")
        return {'processed_count': processed_count}

    except Exception as e:
        logger.error(f"Error in process_pending_webhooks task: {e}")
        return {'error': str(e)}


@shared_task
def sync_mpesa_transaction_status():
    """
    Sync M-Pesa transaction status for pending payments
    Queries Daraja API for transaction status updates
    """
    try:
        # Find M-Pesa transactions that are still processing
        pending_transactions = MpesaTransaction.objects.filter(
            payment__status='processing',
            checkout_request_id__isnull=False,
            created_at__gte=timezone.now() - timedelta(hours=1)  # Only recent ones
        ).select_related('payment')

        updated_count = 0
        mpesa_service = MpesaService()

        for transaction in pending_transactions:
            try:
                result = mpesa_service.query_stk_status(transaction.checkout_request_id)

                if result['success']:
                    data = result['data']
                    transaction.result_code = data.get('ResultCode')
                    transaction.result_desc = data.get('ResultDesc')
                    transaction.save()

                    # Update payment status based on result
                    if data.get('ResultCode') == '0':  # Success
                        transaction.payment.status = 'completed'
                        transaction.payment.payment_date = timezone.now()
                    elif data.get('ResultCode') in ['1032', '1037']:  # User cancelled or timeout
                        transaction.payment.status = 'cancelled'
                    elif data.get('ResultCode'):  # Other error codes
                        transaction.payment.status = 'failed'
                        transaction.payment.failure_reason = data.get('ResultDesc')

                    transaction.payment.save()
                    updated_count += 1

            except Exception as e:
                logger.error(f"Error syncing M-Pesa transaction {transaction.id}: {e}")

        logger.info(f"Synced {updated_count} M-Pesa transaction statuses")
        return {'updated_count': updated_count}

    except Exception as e:
        logger.error(f"Error in sync_mpesa_transaction_status task: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_old_webhooks():
    """
    Clean up old webhook records
    Removes webhook data older than 30 days
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)

        old_webhooks = PaymentWebhook.objects.filter(
            created_at__lt=cutoff_date
        )

        deleted_count = old_webhooks.count()
        old_webhooks.delete()

        logger.info(f"Cleaned up {deleted_count} old webhook records")
        return {'deleted_count': deleted_count}

    except Exception as e:
        logger.error(f"Error in cleanup_old_webhooks task: {e}")
        return {'error': str(e)}


@shared_task
def send_payment_notifications(payment_id, event_type):
    """
    Send payment-related notifications
    Called when payment status changes
    """
    try:
        payment = Payment.objects.get(id=payment_id)

        # This will be enhanced when notifications app is implemented
        logger.info(f"Payment {payment.payment_id} - {event_type}")

        # Placeholder for notification logic
        notifications_sent = 0

        if event_type == 'payment_completed':
            # Send success notification to buyer
            # Send payment received notification to seller
            notifications_sent = 2
        elif event_type == 'payment_failed':
            # Send failure notification to buyer
            notifications_sent = 1
        elif event_type == 'escrow_released':
            # Send payment release notification to seller
            notifications_sent = 1

        return {
            'payment_id': payment.payment_id,
            'event_type': event_type,
            'notifications_sent': notifications_sent
        }

    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found for notification")
        return {'error': 'Payment not found'}
    except Exception as e:
        logger.error(f"Error sending payment notifications: {e}")
        return {'error': str(e)}