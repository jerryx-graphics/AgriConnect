from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from typing import Dict, List, Optional
from .models import Payment, EscrowAccount, PaymentAnalytics
import logging

logger = logging.getLogger(__name__)


class EscrowManager:
    """Utility class for managing escrow operations"""

    @staticmethod
    def create_escrow_for_order(order, payment) -> Optional[EscrowAccount]:
        """Create escrow accounts for all sellers in an order"""
        try:
            escrow_accounts = []

            # Get unique sellers from order items
            sellers = set()
            for item in order.items.select_related('product__farmer'):
                sellers.add(item.product.farmer)

            # For multi-vendor orders, split payment proportionally
            total_order_amount = order.total_amount

            for seller in sellers:
                # Calculate seller's portion of the order
                seller_items = order.items.filter(product__farmer=seller)
                seller_amount = sum(item.quantity * item.price_per_unit for item in seller_items)

                # Calculate proportional payment amount
                escrow_amount = (seller_amount / total_order_amount) * payment.amount

                escrow = EscrowAccount.objects.create(
                    payment=payment,
                    seller=seller,
                    amount=escrow_amount,
                    status='active'
                )
                escrow_accounts.append(escrow)

                logger.info(f"Created escrow account {escrow.id} for seller {seller.id} - Amount: {escrow_amount}")

            return escrow_accounts[0] if escrow_accounts else None

        except Exception as e:
            logger.error(f"Error creating escrow for order {order.id}: {e}")
            return None

    @staticmethod
    def get_escrow_status(payment_id: str) -> Dict:
        """Get escrow status for a payment"""
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            escrow_accounts = EscrowAccount.objects.filter(payment=payment)

            if not escrow_accounts.exists():
                return {
                    'has_escrow': False,
                    'message': 'No escrow accounts found for this payment'
                }

            escrow_data = []
            total_escrowed = 0

            for escrow in escrow_accounts:
                escrow_data.append({
                    'id': str(escrow.id),
                    'seller': escrow.seller.email,
                    'amount': float(escrow.amount),
                    'status': escrow.status,
                    'auto_release_days': escrow.auto_release_days,
                    'days_held': (timezone.now() - escrow.created_at).days,
                    'release_date': escrow.release_date.isoformat() if escrow.release_date else None
                })
                total_escrowed += escrow.amount

            return {
                'has_escrow': True,
                'total_amount': float(payment.amount),
                'total_escrowed': float(total_escrowed),
                'escrow_accounts': escrow_data
            }

        except Payment.DoesNotExist:
            return {
                'has_escrow': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error getting escrow status: {e}")
            return {
                'has_escrow': False,
                'error': str(e)
            }

    @staticmethod
    def release_all_escrow_for_payment(payment_id: str, release_reason: str = '') -> Dict:
        """Release all escrow accounts for a payment"""
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            escrow_accounts = EscrowAccount.objects.filter(
                payment=payment,
                status='active'
            )

            if not escrow_accounts.exists():
                return {
                    'success': False,
                    'message': 'No active escrow accounts found'
                }

            released_count = 0
            total_released = 0

            for escrow in escrow_accounts:
                escrow.status = 'released'
                escrow.release_date = timezone.now()
                escrow.resolution_notes = release_reason
                escrow.save()

                released_count += 1
                total_released += escrow.amount

            # Update payment status
            payment.status = 'completed'
            payment.save()

            return {
                'success': True,
                'released_count': released_count,
                'total_released': float(total_released),
                'message': f'Released {released_count} escrow accounts'
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'message': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error releasing escrow for payment {payment_id}: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    @staticmethod
    def dispute_escrow(escrow_id: str, dispute_reason: str, disputer_id: int) -> Dict:
        """Mark an escrow account as disputed"""
        try:
            escrow = EscrowAccount.objects.get(id=escrow_id)

            if escrow.status != 'active':
                return {
                    'success': False,
                    'message': 'Can only dispute active escrow accounts'
                }

            escrow.status = 'disputed'
            escrow.dispute_reason = dispute_reason
            escrow.dispute_date = timezone.now()
            escrow.save()

            logger.info(f"Escrow {escrow_id} disputed by user {disputer_id}: {dispute_reason}")

            return {
                'success': True,
                'message': 'Escrow marked as disputed. Admin review required.'
            }

        except EscrowAccount.DoesNotExist:
            return {
                'success': False,
                'message': 'Escrow account not found'
            }
        except Exception as e:
            logger.error(f"Error disputing escrow {escrow_id}: {e}")
            return {
                'success': False,
                'message': str(e)
            }


class PaymentAnalyticsCalculator:
    """Utility class for calculating payment analytics"""

    @staticmethod
    def get_payment_summary(start_date=None, end_date=None) -> Dict:
        """Get payment summary for a date range"""
        try:
            if not start_date:
                start_date = timezone.now().date() - timedelta(days=30)
            if not end_date:
                end_date = timezone.now().date()

            payments = Payment.objects.filter(
                created_at__date__range=[start_date, end_date]
            )

            summary = {
                'total_payments': payments.count(),
                'completed_payments': payments.filter(status__in=['completed', 'paid']).count(),
                'failed_payments': payments.filter(status='failed').count(),
                'pending_payments': payments.filter(status__in=['pending', 'processing']).count(),
            }

            # Amount calculations
            completed_payments = payments.filter(status__in=['completed', 'paid'])
            summary['total_amount'] = float(completed_payments.aggregate(
                total=Sum('amount')
            )['total'] or 0)

            # Payment method breakdown
            summary['payment_methods'] = {
                'mpesa': payments.filter(payment_method='mpesa').count(),
                'bank': payments.filter(payment_method='bank').count(),
                'cash': payments.filter(payment_method='cash').count(),
            }

            # Success rate
            if summary['total_payments'] > 0:
                summary['success_rate'] = (summary['completed_payments'] / summary['total_payments']) * 100
            else:
                summary['success_rate'] = 0

            return summary

        except Exception as e:
            logger.error(f"Error calculating payment summary: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_escrow_summary() -> Dict:
        """Get current escrow summary"""
        try:
            escrow_accounts = EscrowAccount.objects.all()

            summary = {
                'total_escrow_accounts': escrow_accounts.count(),
                'active_escrow': escrow_accounts.filter(status='active').count(),
                'released_escrow': escrow_accounts.filter(status='released').count(),
                'disputed_escrow': escrow_accounts.filter(status='disputed').count(),
            }

            # Amount calculations
            summary['total_amount_in_escrow'] = float(escrow_accounts.filter(
                status='active'
            ).aggregate(total=Sum('amount'))['total'] or 0)

            summary['total_amount_released'] = float(escrow_accounts.filter(
                status='released'
            ).aggregate(total=Sum('amount'))['total'] or 0)

            # Average escrow holding time
            released_escrows = escrow_accounts.filter(
                status='released',
                release_date__isnull=False
            )

            if released_escrows.exists():
                total_days = sum([
                    (escrow.release_date.date() - escrow.created_at.date()).days
                    for escrow in released_escrows
                ])
                summary['average_holding_days'] = total_days / released_escrows.count()
            else:
                summary['average_holding_days'] = 0

            return summary

        except Exception as e:
            logger.error(f"Error calculating escrow summary: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_revenue_analytics(start_date=None, end_date=None) -> Dict:
        """Calculate revenue analytics including platform fees"""
        try:
            if not start_date:
                start_date = timezone.now().date() - timedelta(days=30)
            if not end_date:
                end_date = timezone.now().date()

            completed_payments = Payment.objects.filter(
                status__in=['completed', 'paid'],
                created_at__date__range=[start_date, end_date]
            )

            total_revenue = completed_payments.aggregate(
                total=Sum('amount')
            )['total'] or 0

            # Platform fee calculation (3% default)
            platform_fee_rate = 0.03
            platform_fees = total_revenue * platform_fee_rate

            # Daily breakdown
            analytics_data = PaymentAnalytics.objects.filter(
                date__range=[start_date, end_date]
            ).order_by('date')

            daily_data = []
            for analytics in analytics_data:
                daily_data.append({
                    'date': analytics.date.isoformat(),
                    'transactions': analytics.total_transactions,
                    'revenue': float(analytics.total_amount),
                    'fees_collected': float(analytics.total_fees_collected)
                })

            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_revenue': float(total_revenue),
                'platform_fees': float(platform_fees),
                'net_revenue': float(total_revenue - platform_fees),
                'daily_breakdown': daily_data
            }

        except Exception as e:
            logger.error(f"Error calculating revenue analytics: {e}")
            return {'error': str(e)}


def validate_payment_amount(amount: float, order_total: float) -> Dict:
    """Validate payment amount against order total"""
    try:
        if amount <= 0:
            return {
                'valid': False,
                'message': 'Payment amount must be greater than zero'
            }

        if amount != order_total:
            return {
                'valid': False,
                'message': f'Payment amount ({amount}) does not match order total ({order_total})'
            }

        return {'valid': True}

    except Exception as e:
        return {
            'valid': False,
            'message': f'Error validating payment amount: {str(e)}'
        }


def format_mpesa_phone_number(phone_number: str) -> str:
    """Format phone number for M-Pesa API"""
    # Remove any spaces or special characters
    phone = ''.join(filter(str.isdigit, phone_number))

    # Handle different formats
    if phone.startswith('0'):
        return '254' + phone[1:]
    elif phone.startswith('254'):
        return phone
    elif len(phone) == 9:  # Missing country code and leading zero
        return '254' + phone
    else:
        return phone


def calculate_platform_fee(amount: float, fee_rate: float = 0.03) -> float:
    """Calculate platform fee for a payment"""
    return amount * fee_rate