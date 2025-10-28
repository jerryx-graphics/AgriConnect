from django.core.management.base import BaseCommand
from notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        templates = [
            # Order-related templates
            {
                'name': 'Order Created (SMS)',
                'notification_type': 'ORDER_CREATED',
                'channel': 'SMS',
                'message_template': 'Your order #{{order_number}} has been created successfully. Total: KES {{total_amount}}. Track at: {{tracking_url}}'
            },
            {
                'name': 'Order Created (Email)',
                'notification_type': 'ORDER_CREATED',
                'channel': 'EMAIL',
                'subject_template': 'Order Confirmation - {{order_number}}',
                'message_template': 'Dear {{customer_name}},\n\nYour order #{{order_number}} has been created successfully.\n\nOrder Details:\n- Total Amount: KES {{total_amount}}\n- Expected Delivery: {{delivery_date}}\n\nTrack your order: {{tracking_url}}\n\nThank you for choosing AgriConnect!'
            },
            {
                'name': 'Order Confirmed (SMS)',
                'notification_type': 'ORDER_CONFIRMED',
                'channel': 'SMS',
                'message_template': 'Great news! Your order #{{order_number}} has been confirmed by the farmer. Expected delivery: {{delivery_date}}'
            },
            {
                'name': 'Order Shipped (SMS)',
                'notification_type': 'ORDER_SHIPPED',
                'channel': 'SMS',
                'message_template': 'Your order #{{order_number}} is on its way! Transporter: {{transporter_name}}. Track: {{tracking_url}}'
            },
            {
                'name': 'Order Delivered (SMS)',
                'notification_type': 'ORDER_DELIVERED',
                'channel': 'SMS',
                'message_template': 'Your order #{{order_number}} has been delivered! Please rate your experience: {{rating_url}}'
            },
            {
                'name': 'Order Cancelled (SMS)',
                'notification_type': 'ORDER_CANCELLED',
                'channel': 'SMS',
                'message_template': 'Your order #{{order_number}} has been cancelled. Refund will be processed within 3-5 business days. Support: 0700123456'
            },

            # Payment-related templates
            {
                'name': 'Payment Received (SMS)',
                'notification_type': 'PAYMENT_RECEIVED',
                'channel': 'SMS',
                'message_template': 'Payment of KES {{amount}} received for order #{{order_number}}. Transaction ID: {{transaction_id}}'
            },
            {
                'name': 'Payment Failed (SMS)',
                'notification_type': 'PAYMENT_FAILED',
                'channel': 'SMS',
                'message_template': 'Payment for order #{{order_number}} failed. Please try again or contact support: 0700123456'
            },

            # Account-related templates
            {
                'name': 'Account Verified (SMS)',
                'notification_type': 'ACCOUNT_VERIFIED',
                'channel': 'SMS',
                'message_template': 'Welcome to AgriConnect! Your {{role}} account has been verified. Start exploring fresh farm products now!'
            },
            {
                'name': 'Product Approved (SMS)',
                'notification_type': 'PRODUCT_APPROVED',
                'channel': 'SMS',
                'message_template': 'Your product "{{product_name}}" has been approved and is now live on AgriConnect!'
            },
            {
                'name': 'Product Rejected (SMS)',
                'notification_type': 'PRODUCT_REJECTED',
                'channel': 'SMS',
                'message_template': 'Your product "{{product_name}}" needs revision. Reason: {{rejection_reason}}. Please update and resubmit.'
            },

            # In-app notification templates
            {
                'name': 'Order Created (In-App)',
                'notification_type': 'ORDER_CREATED',
                'channel': 'IN_APP',
                'message_template': 'Your order #{{order_number}} for KES {{total_amount}} has been created successfully.'
            },
            {
                'name': 'Order Confirmed (In-App)',
                'notification_type': 'ORDER_CONFIRMED',
                'channel': 'IN_APP',
                'message_template': 'Order #{{order_number}} confirmed by {{farmer_name}}. Expected delivery: {{delivery_date}}'
            },
            {
                'name': 'Payment Received (In-App)',
                'notification_type': 'PAYMENT_RECEIVED',
                'channel': 'IN_APP',
                'message_template': 'Payment of KES {{amount}} received for order #{{order_number}}'
            },

            # Price alert template
            {
                'name': 'Price Alert (SMS)',
                'notification_type': 'PRICE_ALERT',
                'channel': 'SMS',
                'message_template': 'Price alert! {{product_name}} is now available at KES {{price}} per {{unit}} - {{discount}}% off! Check it out: {{product_url}}'
            },

            # Email templates for better formatting
            {
                'name': 'Order Confirmed (Email)',
                'notification_type': 'ORDER_CONFIRMED',
                'channel': 'EMAIL',
                'subject_template': 'Order Confirmed - {{order_number}}',
                'message_template': 'Dear {{customer_name}},\n\nGreat news! Your order has been confirmed.\n\nOrder Details:\n- Order Number: {{order_number}}\n- Farmer: {{farmer_name}}\n- Total Amount: KES {{total_amount}}\n- Expected Delivery: {{delivery_date}}\n\nYour fresh produce will be delivered soon!\n\nBest regards,\nAgriConnect Team'
            },
            {
                'name': 'Payment Received (Email)',
                'notification_type': 'PAYMENT_RECEIVED',
                'channel': 'EMAIL',
                'subject_template': 'Payment Confirmation - {{transaction_id}}',
                'message_template': 'Dear {{customer_name}},\n\nWe have received your payment successfully.\n\nPayment Details:\n- Amount: KES {{amount}}\n- Order: #{{order_number}}\n- Transaction ID: {{transaction_id}}\n- Date: {{payment_date}}\n\nYour order is now being processed.\n\nThank you for choosing AgriConnect!'
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                channel=template_data['channel'],
                defaults=template_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                # Update existing template
                for key, value in template_data.items():
                    setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} new templates, '
                f'updated {updated_count} existing templates.'
            )
        )