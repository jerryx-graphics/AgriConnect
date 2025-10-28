from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from payments.models import Payment
from payments.services import MpesaService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync payment status with external gateways'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours back to check for pending payments'
        )
        parser.add_argument(
            '--payment-method',
            type=str,
            choices=['mpesa', 'bank', 'cash'],
            help='Specific payment method to sync'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )

    def handle(self, **options):
        hours_back = options['hours']
        payment_method = options.get('payment_method')
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(f'Starting payment status sync for last {hours_back} hours...')
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        cutoff_time = timezone.now() - timedelta(hours=hours_back)

        # Build query filters
        filters = {
            'status__in': ['pending', 'processing'],
            'created_at__gte': cutoff_time
        }
        if payment_method:
            filters['payment_method'] = payment_method

        pending_payments = Payment.objects.filter(**filters)

        self.stdout.write(f'Found {pending_payments.count()} pending payments to check')

        updated_count = 0
        error_count = 0

        for payment in pending_payments:
            try:
                if payment.payment_method == 'mpesa':
                    updated = self.sync_mpesa_payment(payment, dry_run)
                elif payment.payment_method == 'bank':
                    updated = self.sync_bank_payment(payment, dry_run)
                elif payment.payment_method == 'cash':
                    updated = self.sync_cash_payment(payment, dry_run)
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Unknown payment method: {payment.payment_method}')
                    )
                    continue

                if updated:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error syncing payment {payment.payment_id}: {str(e)}')
                )
                logger.error(f'Error syncing payment {payment.payment_id}: {e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Sync completed: {updated_count} updated, {error_count} errors'
            )
        )

    def sync_mpesa_payment(self, payment, dry_run=False):
        """Sync M-Pesa payment status"""
        try:
            mpesa_transaction = payment.mpesa_transaction
            if not mpesa_transaction or not mpesa_transaction.checkout_request_id:
                return False

            mpesa_service = MpesaService()
            result = mpesa_service.query_stk_status(mpesa_transaction.checkout_request_id)

            if result['success']:
                data = result['data']
                result_code = data.get('ResultCode')

                self.stdout.write(f'M-Pesa query result for {payment.payment_id}: {result_code}')

                if not dry_run:
                    # Update transaction
                    mpesa_transaction.result_code = str(result_code)
                    mpesa_transaction.result_desc = data.get('ResultDesc')
                    mpesa_transaction.save()

                    # Update payment status
                    if result_code == '0':  # Success
                        payment.status = 'completed'
                        payment.payment_date = timezone.now()
                    elif result_code in ['1032', '1037']:  # Cancelled/timeout
                        payment.status = 'cancelled'
                    else:  # Other failures
                        payment.status = 'failed'
                        payment.failure_reason = data.get('ResultDesc')

                    payment.save()

                return True
            else:
                self.stdout.write(
                    self.style.WARNING(f'Failed to query M-Pesa status: {result["message"]}')
                )
                return False

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing M-Pesa payment: {str(e)}')
            )
            return False

    def sync_bank_payment(self, payment, dry_run=False):
        """Sync bank payment status (manual verification needed)"""
        # Bank payments typically require manual verification
        # This is a placeholder for bank integration
        self.stdout.write(f'Bank payment {payment.payment_id} requires manual verification')
        return False

    def sync_cash_payment(self, payment, dry_run=False):
        """Sync cash payment status"""
        # Cash payments are typically updated when delivery is completed
        # Check if associated order is delivered
        if payment.order and payment.order.status == 'delivered':
            self.stdout.write(f'Cash payment {payment.payment_id} - order delivered, updating status')

            if not dry_run:
                payment.status = 'completed'
                payment.payment_date = timezone.now()
                payment.save()

            return True

        return False