from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Notification, NotificationTemplate, UserNotificationSettings,
    SMSLog, EmailLog, PushNotificationLog
)

User = get_user_model()


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'channel',
            'subject_template', 'message_template', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.notification_type', read_only=True)
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_email', 'template', 'template_name',
            'template_type', 'subject', 'message', 'status', 'channel',
            'sent_at', 'delivered_at', 'read_at', 'external_id',
            'error_message', 'context_data', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'sent_at', 'delivered_at', 'read_at', 'external_id',
            'error_message', 'created_at', 'updated_at'
        ]


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user notification settings"""

    class Meta:
        model = UserNotificationSettings
        fields = [
            'id', 'user', 'sms_enabled', 'sms_order_updates',
            'sms_payment_updates', 'sms_marketing', 'email_enabled',
            'email_order_updates', 'email_payment_updates', 'email_marketing',
            'email_newsletter', 'push_enabled', 'push_order_updates',
            'push_payment_updates', 'push_marketing', 'in_app_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class SMSLogSerializer(serializers.ModelSerializer):
    """Serializer for SMS logs"""
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    template_name = serializers.CharField(source='notification.template.name', read_only=True)

    class Meta:
        model = SMSLog
        fields = [
            'id', 'notification_id', 'template_name', 'phone_number',
            'message_id', 'cost', 'status_code', 'network_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for email logs"""
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    template_name = serializers.CharField(source='notification.template.name', read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            'id', 'notification_id', 'template_name', 'email_address',
            'message_id', 'bounce_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PushNotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for push notification logs"""
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    template_name = serializers.CharField(source='notification.template.name', read_only=True)

    class Meta:
        model = PushNotificationLog
        fields = [
            'id', 'notification_id', 'template_name', 'device_token',
            'platform', 'message_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending custom notifications"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs to send notification to"
    )
    notification_type = serializers.ChoiceField(
        choices=NotificationTemplate.NOTIFICATION_TYPES,
        help_text="Type of notification to send"
    )
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=NotificationTemplate.CHANNELS),
        required=False,
        help_text="Channels to send notification to. If not provided, sends to all active channels"
    )
    context_data = serializers.JSONField(
        required=False,
        help_text="Context data for template rendering"
    )

    def validate_recipient_ids(self, value):
        """Validate that all recipient IDs exist"""
        existing_ids = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(
                f"Users with IDs {list(missing_ids)} do not exist"
            )
        return value


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications to user groups"""
    RECIPIENT_TYPES = [
        ('ALL_USERS', 'All Users'),
        ('FARMERS', 'All Farmers'),
        ('BUYERS', 'All Buyers'),
        ('TRANSPORTERS', 'All Transporters'),
        ('COOPERATIVES', 'All Cooperatives'),
    ]

    recipient_type = serializers.ChoiceField(
        choices=RECIPIENT_TYPES,
        help_text="Type of users to send notification to"
    )
    notification_type = serializers.ChoiceField(
        choices=NotificationTemplate.NOTIFICATION_TYPES,
        help_text="Type of notification to send"
    )
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=NotificationTemplate.CHANNELS),
        required=False,
        help_text="Channels to send notification to"
    )
    context_data = serializers.JSONField(
        required=False,
        help_text="Context data for template rendering"
    )


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of notification IDs to mark as read"
    )

    def validate_notification_ids(self, value):
        """Validate that all notification IDs exist and belong to the user"""
        user = self.context['request'].user
        existing_ids = Notification.objects.filter(
            id__in=value,
            recipient=user,
            channel='IN_APP'
        ).values_list('id', flat=True)

        missing_ids = set(value) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(
                f"Notifications with IDs {list(missing_ids)} do not exist or cannot be marked as read"
            )
        return value