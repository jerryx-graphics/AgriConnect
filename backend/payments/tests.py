from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
from .models import (
    Payment, MpesaTransaction, EscrowAccount,
    PaymentWebhook, PaymentRefund
)
from .services import MpesaService, PaymentProcessingService
from .utils import EscrowManager, validate_payment_amount, format_mpesa_phone_number
from orders.models import Order, OrderItem
from products.models import Product, ProductCategory
from users.models import FarmerProfile

User = get_user_model()


class PaymentModelTests(TestCase):
    """Test payment models"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='buyer'
        )

        # Create a farmer
        self.farmer = User.objects.create_user(
            email='farmer@example.com',
            password='testpass123',
            role='farmer'
        )

        # Create farmer profile
        self.farmer_profile = FarmerProfile.objects.create(
            user=self.farmer,
            farm_name='Test Farm',
            farm_size_acres=10.0,
            county='Kisii',
            sub_county='Nyaribari Masaba'
        )

        # Create product category
        self.category = ProductCategory.objects.create(
            name='Vegetables',
            description='Fresh vegetables'
        )

        # Create product
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Tomatoes',
            description='Fresh tomatoes',
            price_per_unit=Decimal('50.00'),
            unit='kg',
            available_quantity=100,
            county='Kisii'
        )

        # Create order
        self.order = Order.objects.create(
            buyer=self.user,
            subtotal=Decimal('500.00'),
            delivery_fee=Decimal('100.00'),
            platform_fee=Decimal('18.00'),
            total_amount=Decimal('618.00'),
            delivery_address='Test Address',
            delivery_county='Kisii',
            delivery_phone='+254712345678'
        )

        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            price_per_unit=Decimal('50.00')
        )

    def test_payment_creation(self):
        """Test payment model creation"""
        payment = Payment.objects.create(
            order=self.order,
            payer=self.user,
            amount=Decimal('618.00'),
            payment_method='mpesa'
        )

        self.assertEqual(payment.payer, self.user)
        self.assertEqual(payment.amount, Decimal('618.00'))
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.currency, 'KES')
        self.assertTrue(payment.payment_id.startswith('TXN'))

    def test_mpesa_transaction_creation(self):
        """Test M-Pesa transaction creation"""
        payment = Payment.objects.create(
            order=self.order,
            payer=self.user,
            amount=Decimal('618.00'),
            payment_method='mpesa'
        )

        mpesa_transaction = MpesaTransaction.objects.create(
            payment=payment,
            phone_number='+254712345678',
            transaction_type='paybill'
        )

        self.assertEqual(mpesa_transaction.payment, payment)
        self.assertEqual(mpesa_transaction.phone_number, '+254712345678')
        self.assertEqual(mpesa_transaction.transaction_type, 'paybill')

    def test_escrow_account_creation(self):
        """Test escrow account creation"""
        payment = Payment.objects.create(
            order=self.order,
            payer=self.user,
            amount=Decimal('618.00'),
            payment_method='mpesa'
        )

        escrow = EscrowAccount.objects.create(
            payment=payment,
            seller=self.farmer,
            amount=Decimal('500.00')
        )

        self.assertEqual(escrow.payment, payment)
        self.assertEqual(escrow.seller, self.farmer)
        self.assertEqual(escrow.amount, Decimal('500.00'))
        self.assertEqual(escrow.status, 'active')
        self.assertEqual(escrow.auto_release_days, 7)


class MpesaServiceTests(TestCase):
    """Test M-Pesa service integration"""

    def setUp(self):
        self.mpesa_service = MpesaService()

    @patch('payments.services.requests.get')
    def test_get_access_token_success(self, mock_get):
        """Test successful access token retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'test_token_123'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        token = self.mpesa_service.get_access_token()
        self.assertEqual(token, 'test_token_123')

    @patch('payments.services.requests.get')
    def test_get_access_token_failure(self, mock_get):
        """Test access token retrieval failure"""
        mock_get.side_effect = Exception('Network error')

        token = self.mpesa_service.get_access_token()
        self.assertIsNone(token)

    def test_generate_password(self):
        """Test password generation for STK push"""
        password, timestamp = self.mpesa_service.generate_password()

        self.assertIsInstance(password, str)
        self.assertIsInstance(timestamp, str)
        self.assertEqual(len(timestamp), 14)  # Format: YYYYMMDDHHMMSS

    def test_format_phone_number(self):
        """Test phone number formatting"""
        # Test various phone number formats
        test_cases = [
            ('0712345678', '254712345678'),
            ('+254712345678', '254712345678'),
            ('254712345678', '254712345678'),
            ('712345678', '254712345678'),
        ]

        for input_phone, expected in test_cases:
            formatted = format_mpesa_phone_number(input_phone)
            self.assertEqual(formatted, expected)

    def test_process_callback_success(self):
        """Test processing successful M-Pesa callback"""
        callback_data = {
            'Body': {
                'stkCallback': {
                    'MerchantRequestID': 'merchant_123',
                    'CheckoutRequestID': 'checkout_123',
                    'ResultCode': 0,
                    'ResultDesc': 'The service request is processed successfully.',
                    'CallbackMetadata': {
                        'Item': [
                            {'Name': 'Amount', 'Value': 618.0},
                            {'Name': 'MpesaReceiptNumber', 'Value': 'ABC123'},
                            {'Name': 'TransactionDate', 'Value': 20231227140000},
                            {'Name': 'PhoneNumber', 'Value': 254712345678}
                        ]
                    }
                }
            }
        }

        processed = self.mpesa_service.process_callback(callback_data)

        self.assertTrue(processed['success'])
        self.assertEqual(processed['merchant_request_id'], 'merchant_123')
        self.assertEqual(processed['checkout_request_id'], 'checkout_123')
        self.assertEqual(processed['result_code'], '0')
        self.assertEqual(processed['metadata']['amount'], 618.0)
        self.assertEqual(processed['metadata']['mpesa_receipt_number'], 'ABC123')

    def test_process_callback_failure(self):
        """Test processing failed M-Pesa callback"""
        callback_data = {
            'Body': {
                'stkCallback': {
                    'MerchantRequestID': 'merchant_123',
                    'CheckoutRequestID': 'checkout_123',
                    'ResultCode': 1032,
                    'ResultDesc': 'Request cancelled by user'
                }
            }
        }

        processed = self.mpesa_service.process_callback(callback_data)

        self.assertFalse(processed['success'])
        self.assertEqual(processed['result_code'], '1032')
        self.assertEqual(processed['result_desc'], 'Request cancelled by user')


class PaymentUtilityTests(TestCase):
    """Test payment utility functions"""

    def test_validate_payment_amount_valid(self):
        """Test valid payment amount validation"""
        result = validate_payment_amount(100.0, 100.0)
        self.assertTrue(result['valid'])

    def test_validate_payment_amount_invalid_zero(self):
        """Test invalid zero payment amount"""
        result = validate_payment_amount(0.0, 100.0)
        self.assertFalse(result['valid'])
        self.assertIn('greater than zero', result['message'])

    def test_validate_payment_amount_mismatch(self):
        """Test payment amount mismatch"""
        result = validate_payment_amount(90.0, 100.0)
        self.assertFalse(result['valid'])
        self.assertIn('does not match', result['message'])

    def test_format_mpesa_phone_number(self):
        """Test M-Pesa phone number formatting"""
        test_cases = [
            ('0712345678', '254712345678'),
            ('+254712345678', '254712345678'),
            ('254712345678', '254712345678'),
        ]

        for input_phone, expected in test_cases:
            result = format_mpesa_phone_number(input_phone)
            self.assertEqual(result, expected)
