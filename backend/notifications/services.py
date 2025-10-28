import logging
import requests
from typing import Dict, List, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from .models import (
    Notification, NotificationTemplate, SMSLog, EmailLog,
    PushNotificationLog, UserNotificationSettings
)

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Main notification service for sending various types of notifications"""

    @staticmethod
    def send_notification(
        user: User,
        notification_type: str,
        context_data: Dict = None,
        channels: List[str] = None
    ) -> List[Notification]:
        """
        Send notification to user across specified channels

        Args:
            user: User to send notification to
            notification_type: Type of notification (from NotificationTemplate.NOTIFICATION_TYPES)
            context_data: Data to populate template variables
            channels: List of channels to send to. If None, sends to all active channels

        Returns:
            List of created Notification objects
        """
        if context_data is None:
            context_data = {}

        # Get user notification settings
        settings_obj, _ = UserNotificationSettings.objects.get_or_create(user=user)

        # Get templates for the notification type
        templates = NotificationTemplate.objects.filter(
            notification_type=notification_type,
            is_active=True
        )

        if channels:
            templates = templates.filter(channel__in=channels)

        notifications = []

        for template in templates:
            # Check if user has enabled this channel and type
            if not NotificationService._should_send_notification(settings_obj, template):
                continue

            # Render the message
            rendered_subject, rendered_message = NotificationService._render_template(
                template, context_data
            )

            # Create notification record
            notification = Notification.objects.create(
                recipient=user,
                template=template,
                subject=rendered_subject,
                message=rendered_message,
                channel=template.channel,
                context_data=context_data
            )

            # Send notification asynchronously
            send_notification_task.delay(notification.id)
            notifications.append(notification)

        return notifications

    @staticmethod
    def _should_send_notification(settings: UserNotificationSettings, template: NotificationTemplate) -> bool:
        """Check if notification should be sent based on user preferences"""
        channel = template.channel
        notification_type = template.notification_type

        # Check if channel is enabled
        if channel == 'SMS' and not settings.sms_enabled:
            return False
        elif channel == 'EMAIL' and not settings.email_enabled:
            return False
        elif channel == 'PUSH' and not settings.push_enabled:
            return False
        elif channel == 'IN_APP' and not settings.in_app_enabled:
            return False

        # Check specific notification type preferences
        if notification_type in ['ORDER_CREATED', 'ORDER_CONFIRMED', 'ORDER_SHIPPED', 'ORDER_DELIVERED', 'ORDER_CANCELLED']:
            if channel == 'SMS' and not settings.sms_order_updates:
                return False
            elif channel == 'EMAIL' and not settings.email_order_updates:
                return False
            elif channel == 'PUSH' and not settings.push_order_updates:
                return False

        elif notification_type in ['PAYMENT_RECEIVED', 'PAYMENT_FAILED']:
            if channel == 'SMS' and not settings.sms_payment_updates:
                return False
            elif channel == 'EMAIL' and not settings.email_payment_updates:
                return False
            elif channel == 'PUSH' and not settings.push_payment_updates:
                return False

        return True

    @staticmethod
    def _render_template(template: NotificationTemplate, context_data: Dict) -> tuple:
        """Render template with context data"""
        context = Context(context_data)

        subject = ""
        if template.subject_template:
            subject_template = Template(template.subject_template)
            subject = subject_template.render(context)

        message_template = Template(template.message_template)
        message = message_template.render(context)

        return subject, message


class SMSService:
    """Service for sending SMS notifications using Africa's Talking API"""

    def __init__(self):
        self.username = getattr(settings, 'AFRICASTALKING_USERNAME', '')
        self.api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        self.sender_id = getattr(settings, 'AFRICASTALKING_SENDER_ID', 'AgriConnect')
        self.base_url = "https://api.africastalking.com/version1/messaging"

    def send_sms(self, notification: Notification) -> bool:
        """Send SMS notification"""
        try:
            phone_number = notification.recipient.phone_number
            if not phone_number:
                notification.mark_as_failed("User has no phone number")
                return False

            # Format phone number for Kenya (+254)
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            elif not phone_number.startswith('+'):
                phone_number = '+254' + phone_number

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'apiKey': self.api_key
            }

            data = {
                'username': self.username,
                'to': phone_number,
                'message': notification.message,
                'from': self.sender_id
            }

            response = requests.post(self.base_url, headers=headers, data=data)
            response.raise_for_status()

            response_data = response.json()
            sms_data = response_data.get('SMSMessageData', {})
            recipients = sms_data.get('Recipients', [])

            if recipients and len(recipients) > 0:
                recipient_data = recipients[0]
                message_id = recipient_data.get('messageId', '')
                status_code = recipient_data.get('statusCode')
                cost = recipient_data.get('cost', '0')

                # Log SMS details
                SMSLog.objects.create(
                    notification=notification,
                    phone_number=phone_number,
                    message_id=message_id,
                    cost=float(cost.replace('KES ', '')) if cost.startswith('KES') else 0,
                    status_code=str(status_code),
                )

                if status_code == 101:  # Success
                    notification.mark_as_sent(message_id)
                    return True
                else:
                    notification.mark_as_failed(f"SMS failed with status code: {status_code}")
                    return False

        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            notification.mark_as_failed(str(e))
            return False


class EmailService:
    """Service for sending email notifications using SendGrid"""

    def __init__(self):
        self.sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.use_sendgrid = bool(self.sendgrid_api_key)

    def send_email(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            recipient_email = notification.recipient.email
            if not recipient_email:
                notification.mark_as_failed("User has no email address")
                return False

            # Log email attempt
            email_log = EmailLog.objects.create(
                notification=notification,
                email_address=recipient_email
            )

            if self.use_sendgrid:
                return self._send_with_sendgrid(notification, email_log)
            else:
                return self._send_with_django(notification, email_log)

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            notification.mark_as_failed(str(e))
            return False

    def _send_with_sendgrid(self, notification: Notification, email_log: EmailLog) -> bool:
        """Send email using SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail

            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

            # Create HTML version of the message
            html_message = notification.message.replace('\n', '<br>')

            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=notification.recipient.email,
                subject=notification.subject or "AgriConnect Notification",
                html_content=f"""
                <html>
                <body>
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #2E7D32; color: white; padding: 20px; text-align: center;">
                            <h1>AgriConnect</h1>
                        </div>
                        <div style="padding: 20px; background-color: #f9f9f9;">
                            {html_message}
                        </div>
                        <div style="background-color: #E8F5E8; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                            <p>This email was sent by AgriConnect - Connecting Farmers to Markets</p>
                            <p>If you no longer wish to receive these emails, please update your notification preferences in your account settings.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                plain_text_content=notification.message
            )

            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                # Extract message ID from headers if available
                message_id = response.headers.get('X-Message-Id', '')
                email_log.message_id = message_id
                email_log.save()

                notification.mark_as_sent(message_id)
                logger.info(f"Email sent successfully via SendGrid: {message_id}")
                return True
            else:
                error_msg = f"SendGrid returned status {response.status_code}"
                email_log.bounce_reason = error_msg
                email_log.save()
                notification.mark_as_failed(error_msg)
                return False

        except ImportError:
            logger.warning("SendGrid library not installed, falling back to Django email backend")
            return self._send_with_django(notification, email_log)
        except Exception as e:
            logger.error(f"SendGrid email sending failed: {str(e)}")
            email_log.bounce_reason = str(e)
            email_log.save()
            notification.mark_as_failed(str(e))
            return False

    def _send_with_django(self, notification: Notification, email_log: EmailLog) -> bool:
        """Send email using Django's email backend"""
        try:
            # Send email using Django's email backend
            success = send_mail(
                subject=notification.subject or "AgriConnect Notification",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False
            )

            if success:
                notification.mark_as_sent()
                logger.info("Email sent successfully via Django backend")
                return True
            else:
                notification.mark_as_failed("Failed to send email via Django backend")
                return False

        except Exception as e:
            logger.error(f"Django email sending failed: {str(e)}")
            notification.mark_as_failed(str(e))
            return False


class PushNotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging"""

    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_enabled = bool(self.fcm_server_key)

    def send_push_notification(self, notification: Notification) -> bool:
        """Send push notification"""
        try:
            # Get user's device tokens (this would come from a separate DeviceToken model)
            device_tokens = self._get_user_device_tokens(notification.recipient)

            if not device_tokens:
                notification.mark_as_failed("User has no registered devices")
                return False

            success_count = 0
            for device_token_info in device_tokens:
                if self._send_to_device(notification, device_token_info):
                    success_count += 1

            if success_count > 0:
                notification.mark_as_sent(f"Sent to {success_count} devices")
                return True
            else:
                notification.mark_as_failed("Failed to send to any device")
                return False

        except Exception as e:
            logger.error(f"Push notification failed: {str(e)}")
            notification.mark_as_failed(str(e))
            return False

    def _get_user_device_tokens(self, user) -> List[Dict]:
        """Get device tokens for user (placeholder - would need DeviceToken model)"""
        # This is a placeholder implementation
        # In a real app, you'd have a DeviceToken model linked to users
        return [
            {'token': 'placeholder_android_token', 'platform': 'ANDROID'},
            {'token': 'placeholder_ios_token', 'platform': 'IOS'}
        ]

    def _send_to_device(self, notification: Notification, device_info: Dict) -> bool:
        """Send push notification to a specific device"""
        try:
            device_token = device_info['token']
            platform = device_info['platform']

            if self.fcm_enabled:
                return self._send_via_fcm(notification, device_token, platform)
            else:
                return self._send_placeholder(notification, device_token, platform)

        except Exception as e:
            logger.error(f"Failed to send to device {device_info}: {str(e)}")
            return False

    def _send_via_fcm(self, notification: Notification, device_token: str, platform: str) -> bool:
        """Send via Firebase Cloud Messaging"""
        try:
            import requests

            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'to': device_token,
                'notification': {
                    'title': notification.subject or 'AgriConnect',
                    'body': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
                    'icon': 'ic_notification',
                    'color': '#2E7D32',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                },
                'data': {
                    'notification_id': str(notification.id),
                    'type': notification.template.notification_type,
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                }
            }

            response = requests.post(
                'https://fcm.googleapis.com/fcm/send',
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('results', [{}])[0].get('message_id', '')

                # Log the push notification
                PushNotificationLog.objects.create(
                    notification=notification,
                    device_token=device_token,
                    platform=platform,
                    message_id=message_id
                )

                logger.info(f"Push notification sent via FCM: {message_id}")
                return True
            else:
                logger.error(f"FCM returned status {response.status_code}: {response.text}")
                return False

        except ImportError:
            logger.warning("Requests library required for FCM push notifications")
            return self._send_placeholder(notification, device_token, platform)
        except Exception as e:
            logger.error(f"FCM push notification failed: {str(e)}")
            return False

    def _send_placeholder(self, notification: Notification, device_token: str, platform: str) -> bool:
        """Placeholder implementation for development"""
        try:
            # Log the push notification attempt
            PushNotificationLog.objects.create(
                notification=notification,
                device_token=device_token,
                platform=platform,
                message_id=f"placeholder_{timezone.now().timestamp()}"
            )

            logger.info(f"Push notification placeholder sent to {platform} device: {notification.message[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Placeholder push notification failed: {str(e)}")
            return False


@shared_task
def send_notification_task(notification_id: int):
    """Celery task for sending notifications asynchronously"""
    try:
        notification = Notification.objects.get(id=notification_id)

        if notification.channel == 'SMS':
            sms_service = SMSService()
            sms_service.send_sms(notification)
        elif notification.channel == 'EMAIL':
            email_service = EmailService()
            email_service.send_email(notification)
        elif notification.channel == 'PUSH':
            push_service = PushNotificationService()
            push_service.send_push_notification(notification)
        elif notification.channel == 'IN_APP':
            # In-app notifications are just stored in database
            notification.mark_as_sent()

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {str(e)}")


@shared_task
def cleanup_old_notifications():
    """Celery task to cleanup old notifications"""
    from datetime import timedelta
    cutoff_date = timezone.now() - timedelta(days=90)

    # Delete old notifications that are not in-app or unread
    old_notifications = Notification.objects.filter(
        created_at__lt=cutoff_date
    ).exclude(
        channel='IN_APP',
        status__in=['PENDING', 'SENT']
    )

    count = old_notifications.count()
    old_notifications.delete()

    logger.info(f"Cleaned up {count} old notifications")
    return count


# Utility functions for easy notification sending
def send_order_notification(order, notification_type: str, additional_context: Dict = None):
    """Send order-related notifications"""
    context = {
        'order_number': order.order_number,
        'total_amount': order.total_amount,
        'customer_name': order.user.get_full_name() or order.user.email,
        'delivery_date': order.expected_delivery_date.strftime('%B %d, %Y') if order.expected_delivery_date else 'TBD',
        'tracking_url': f"https://app.agriconnect.co.ke/orders/{order.id}/track",
        'rating_url': f"https://app.agriconnect.co.ke/orders/{order.id}/rate",
    }

    if additional_context:
        context.update(additional_context)

    return NotificationService.send_notification(
        user=order.user,
        notification_type=notification_type,
        context_data=context
    )


def send_payment_notification(payment, notification_type: str, additional_context: Dict = None):
    """Send payment-related notifications"""
    context = {
        'amount': payment.amount,
        'transaction_id': payment.transaction_id,
        'order_number': payment.order.order_number if payment.order else 'N/A',
        'payment_date': payment.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'customer_name': payment.user.get_full_name() or payment.user.email,
    }

    if additional_context:
        context.update(additional_context)

    return NotificationService.send_notification(
        user=payment.user,
        notification_type=notification_type,
        context_data=context
    )


def send_product_notification(product, notification_type: str, additional_context: Dict = None):
    """Send product-related notifications"""
    context = {
        'product_name': product.name,
        'farmer_name': product.farmer.get_full_name() or product.farmer.email,
        'price': product.price_per_unit,
        'unit': product.unit_of_measurement,
        'product_url': f"https://app.agriconnect.co.ke/products/{product.id}",
    }

    if additional_context:
        context.update(additional_context)

    return NotificationService.send_notification(
        user=product.farmer,
        notification_type=notification_type,
        context_data=context
    )


def send_account_notification(user, notification_type: str, additional_context: Dict = None):
    """Send account-related notifications"""
    context = {
        'user_name': user.get_full_name() or user.email,
        'role': user.role.title() if hasattr(user, 'role') else 'User',
    }

    if additional_context:
        context.update(additional_context)

    return NotificationService.send_notification(
        user=user,
        notification_type=notification_type,
        context_data=context
    )


def send_price_alert(user, product, old_price: float, new_price: float, discount_percentage: float):
    """Send price alert notification"""
    context = {
        'product_name': product.name,
        'price': new_price,
        'unit': product.unit_of_measurement,
        'old_price': old_price,
        'discount': int(discount_percentage),
        'product_url': f"https://app.agriconnect.co.ke/products/{product.id}",
    }

    return NotificationService.send_notification(
        user=user,
        notification_type='PRICE_ALERT',
        context_data=context,
        channels=['SMS', 'IN_APP']  # Only send via SMS and in-app for price alerts
    )