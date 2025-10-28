from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import BaseModel

User = get_user_model()


class NotificationTemplate(BaseModel):
    """Template for different types of notifications"""
    NOTIFICATION_TYPES = [
        ('ORDER_CREATED', 'Order Created'),
        ('ORDER_CONFIRMED', 'Order Confirmed'),
        ('ORDER_SHIPPED', 'Order Shipped'),
        ('ORDER_DELIVERED', 'Order Delivered'),
        ('ORDER_CANCELLED', 'Order Cancelled'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('PRODUCT_APPROVED', 'Product Approved'),
        ('PRODUCT_REJECTED', 'Product Rejected'),
        ('ACCOUNT_VERIFIED', 'Account Verified'),
        ('PRICE_ALERT', 'Price Alert'),
        ('CUSTOM', 'Custom Message'),
    ]

    CHANNELS = [
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]

    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNELS)
    subject_template = models.CharField(max_length=200, blank=True, help_text="For email notifications")
    message_template = models.TextField(help_text="Use {variable_name} for dynamic content")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['notification_type', 'channel']

    def __str__(self):
        return f"{self.name} ({self.channel})"


class Notification(BaseModel):
    """Individual notification record"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('READ', 'Read'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    channel = models.CharField(max_length=10, choices=NotificationTemplate.CHANNELS)

    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # External service tracking
    external_id = models.CharField(max_length=100, blank=True, help_text="ID from external service")
    error_message = models.TextField(blank=True)

    # Context data
    context_data = models.JSONField(default=dict, help_text="Additional context for the notification")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.channel} to {self.recipient.email} - {self.template.name}"

    def mark_as_sent(self, external_id=None):
        """Mark notification as sent"""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        if external_id:
            self.external_id = external_id
        self.save()

    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save()

    def mark_as_failed(self, error_message):
        """Mark notification as failed"""
        self.status = 'FAILED'
        self.error_message = error_message
        self.save()

    def mark_as_read(self):
        """Mark notification as read (for in-app notifications)"""
        if self.channel == 'IN_APP':
            self.status = 'READ'
            self.read_at = timezone.now()
            self.save()


class SMSLog(BaseModel):
    """Log for SMS notifications using Africa's Talking"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    message_id = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    status_code = models.CharField(max_length=10, blank=True)
    network_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"SMS to {self.phone_number} - {self.notification.template.name}"


class EmailLog(BaseModel):
    """Log for email notifications using SendGrid"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    email_address = models.EmailField()
    message_id = models.CharField(max_length=100, blank=True)
    bounce_reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Email to {self.email_address} - {self.notification.template.name}"


class PushNotificationLog(BaseModel):
    """Log for push notifications"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    device_token = models.CharField(max_length=255)
    platform = models.CharField(max_length=10, choices=[('IOS', 'iOS'), ('ANDROID', 'Android')])
    message_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Push to {self.platform} device - {self.notification.template.name}"


class UserNotificationSettings(BaseModel):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')

    # SMS preferences
    sms_enabled = models.BooleanField(default=True)
    sms_order_updates = models.BooleanField(default=True)
    sms_payment_updates = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_order_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=True)

    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_order_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_marketing = models.BooleanField(default=False)

    # In-app notification preferences
    in_app_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification Settings for {self.user.email}"
