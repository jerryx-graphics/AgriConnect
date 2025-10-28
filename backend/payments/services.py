import requests
import base64
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as django_timezone
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MpesaService:
    """M-Pesa Daraja API integration service"""

    def __init__(self):
        self.environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.callback_url = getattr(settings, 'MPESA_CALLBACK_URL', '')

        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'

    def get_access_token(self) -> Optional[str]:
        """Get OAuth access token from M-Pesa API"""
        try:
            # Create authorization string
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

            # Make request
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get('access_token')

        except requests.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting access token: {e}")
            return None

    def generate_password(self) -> Tuple[str, str]:
        """Generate password and timestamp for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
        return password, timestamp

    def initiate_stk_push(self, phone_number: str, amount: float,
                         account_reference: str, transaction_desc: str) -> Dict:
        """Initiate STK push payment request"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'message': 'Failed to get access token'
                }

            # Format phone number (ensure it starts with 254)
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number

            password, timestamp = self.generate_password()

            # Prepare request data
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),  # M-Pesa expects integer
                'PartyA': phone_number,
                'PartyB': self.shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': self.callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'message': 'STK push initiated successfully',
                    'checkout_request_id': response_data.get('CheckoutRequestID'),
                    'merchant_request_id': response_data.get('MerchantRequestID'),
                    'response_code': response_data.get('ResponseCode'),
                    'response_description': response_data.get('ResponseDescription'),
                    'customer_message': response_data.get('CustomerMessage')
                }
            else:
                return {
                    'success': False,
                    'message': response_data.get('ResponseDescription', 'STK push failed'),
                    'response_code': response_data.get('ResponseCode'),
                    'error_code': response_data.get('errorCode'),
                    'error_message': response_data.get('errorMessage')
                }

        except requests.RequestException as e:
            logger.error(f"STK push request failed: {e}")
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in STK push: {e}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }

    def query_stk_status(self, checkout_request_id: str) -> Dict:
        """Query the status of an STK push transaction"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'message': 'Failed to get access token'
                }

            password, timestamp = self.generate_password()

            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()

            return {
                'success': response.status_code == 200,
                'data': response_data
            }

        except requests.RequestException as e:
            logger.error(f"STK query request failed: {e}")
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in STK query: {e}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }

    def process_callback(self, callback_data: Dict) -> Dict:
        """Process M-Pesa callback data"""
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})

            merchant_request_id = stk_callback.get('MerchantRequestID')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')

            # Extract metadata if payment was successful
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            metadata_items = callback_metadata.get('Item', [])

            processed_data = {
                'merchant_request_id': merchant_request_id,
                'checkout_request_id': checkout_request_id,
                'result_code': str(result_code),
                'result_desc': result_desc,
                'success': result_code == 0,
                'metadata': {}
            }

            # Parse metadata items
            for item in metadata_items:
                name = item.get('Name')
                value = item.get('Value')

                if name == 'Amount':
                    processed_data['metadata']['amount'] = float(value)
                elif name == 'MpesaReceiptNumber':
                    processed_data['metadata']['mpesa_receipt_number'] = value
                elif name == 'TransactionDate':
                    # Convert timestamp to datetime
                    if value:
                        try:
                            processed_data['metadata']['transaction_date'] = datetime.fromtimestamp(
                                int(value), tz=timezone.utc
                            )
                        except (ValueError, TypeError):
                            processed_data['metadata']['transaction_date'] = None
                elif name == 'PhoneNumber':
                    processed_data['metadata']['phone_number'] = value
                elif name == 'Balance':
                    processed_data['metadata']['balance'] = float(value) if value else None

            return processed_data

        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def validate_callback_ip(self, request_ip: str) -> bool:
        """Validate that callback is coming from M-Pesa servers"""
        # M-Pesa callback IP ranges (update as needed)
        allowed_ips = [
            '196.201.214.200',
            '196.201.214.206',
            '196.201.213.114',
            '196.201.214.207',
            '196.201.214.208',
            '196.201.213.44',
            '196.201.212.127',
            '196.201.212.138',
            '196.201.212.129',
            '196.201.212.136',
            '196.201.212.74'
        ]

        # For sandbox, allow localhost and common development IPs
        if self.environment == 'sandbox':
            allowed_ips.extend([
                '127.0.0.1',
                '::1',
                '0.0.0.0'
            ])

        return request_ip in allowed_ips


class PaymentProcessingService:
    """Service for processing payments and managing escrow"""

    def __init__(self):
        self.mpesa_service = MpesaService()

    def initiate_payment(self, payment_obj, phone_number: str = None) -> Dict:
        """Initiate payment based on payment method"""
        try:
            if payment_obj.payment_method == 'mpesa':
                if not phone_number:
                    return {
                        'success': False,
                        'message': 'Phone number required for M-Pesa payment'
                    }

                return self._initiate_mpesa_payment(payment_obj, phone_number)

            elif payment_obj.payment_method == 'bank':
                return self._initiate_bank_payment(payment_obj)

            elif payment_obj.payment_method == 'cash':
                return self._initiate_cash_payment(payment_obj)

            else:
                return {
                    'success': False,
                    'message': 'Unsupported payment method'
                }

        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            return {
                'success': False,
                'message': f'Payment initiation failed: {str(e)}'
            }

    def _initiate_mpesa_payment(self, payment_obj, phone_number: str) -> Dict:
        """Initiate M-Pesa payment"""
        # Create M-Pesa transaction record
        from .models import MpesaTransaction

        mpesa_transaction = MpesaTransaction.objects.create(
            payment=payment_obj,
            phone_number=phone_number,
            transaction_type='paybill'
        )

        # Initiate STK push
        result = self.mpesa_service.initiate_stk_push(
            phone_number=phone_number,
            amount=float(payment_obj.amount),
            account_reference=payment_obj.payment_id,
            transaction_desc=f"Payment for order {payment_obj.order.order_id}"
        )

        if result['success']:
            # Update M-Pesa transaction with response data
            mpesa_transaction.checkout_request_id = result.get('checkout_request_id')
            mpesa_transaction.merchant_request_id = result.get('merchant_request_id')
            mpesa_transaction.save()

            # Update payment status
            payment_obj.status = 'processing'
            payment_obj.save()

        return result

    def _initiate_bank_payment(self, payment_obj) -> Dict:
        """Initiate bank transfer payment"""
        # For now, mark as pending manual verification
        payment_obj.status = 'pending'
        payment_obj.description = 'Awaiting bank transfer confirmation'
        payment_obj.save()

        return {
            'success': True,
            'message': 'Bank payment initiated. Please transfer funds and provide reference.',
            'bank_details': {
                'account_name': 'AgriConnect Kenya Ltd',
                'account_number': '1234567890',
                'bank_name': 'Equity Bank',
                'branch': 'Kisii Branch',
                'reference': payment_obj.payment_id
            }
        }

    def _initiate_cash_payment(self, payment_obj) -> Dict:
        """Initiate cash on delivery payment"""
        payment_obj.status = 'pending'
        payment_obj.description = 'Cash on delivery - Payment due upon delivery'
        payment_obj.save()

        return {
            'success': True,
            'message': 'Cash on delivery payment set up. Pay upon delivery.',
            'instructions': 'Please have exact change ready for the delivery agent.'
        }

    def create_escrow_account(self, payment_obj, seller_id: int) -> Dict:
        """Create escrow account for secure payment"""
        try:
            from .models import EscrowAccount
            from django.contrib.auth import get_user_model

            User = get_user_model()
            seller = User.objects.get(id=seller_id)

            escrow = EscrowAccount.objects.create(
                payment=payment_obj,
                seller=seller,
                amount=payment_obj.amount,
                status='active'
            )

            return {
                'success': True,
                'message': 'Escrow account created successfully',
                'escrow_id': str(escrow.id)
            }

        except Exception as e:
            logger.error(f"Error creating escrow account: {e}")
            return {
                'success': False,
                'message': f'Failed to create escrow account: {str(e)}'
            }

    def release_escrow_funds(self, escrow_id: str, release_reason: str = '') -> Dict:
        """Release funds from escrow to seller"""
        try:
            from .models import EscrowAccount

            escrow = EscrowAccount.objects.get(id=escrow_id)

            if escrow.status != 'active':
                return {
                    'success': False,
                    'message': 'Escrow account is not active'
                }

            escrow.status = 'released'
            escrow.release_date = django_timezone.now()
            escrow.resolution_notes = release_reason
            escrow.save()

            # Update payment status
            escrow.payment.status = 'completed'
            escrow.payment.save()

            return {
                'success': True,
                'message': 'Escrow funds released successfully'
            }

        except Exception as e:
            logger.error(f"Error releasing escrow funds: {e}")
            return {
                'success': False,
                'message': f'Failed to release escrow funds: {str(e)}'
            }