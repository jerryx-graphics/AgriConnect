from django.contrib import admin
from .models import (
    NotificationTemplate, Notification, UserNotificationSettings,
    SMSLog, EmailLog, PushNotificationLog
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'channel', 'is_active', 'created_at']
    list_filter = ['notification_type', 'channel', 'is_active']
    search_fields = ['name', 'message_template']
    ordering = ['notification_type', 'channel']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'template', 'channel', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'channel', 'template__notification_type', 'sent_at']
    search_fields = ['recipient__email', 'recipient__phone_number', 'message']
    readonly_fields = ['sent_at', 'delivered_at', 'read_at', 'external_id']
    ordering = ['-created_at']
    raw_id_fields = ['recipient']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'template')


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'sms_enabled', 'email_enabled', 'push_enabled', 'in_app_enabled']
    list_filter = ['sms_enabled', 'email_enabled', 'push_enabled', 'in_app_enabled']
    search_fields = ['user__email', 'user__phone_number']
    raw_id_fields = ['user']


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'phone_number', 'status_code', 'cost', 'created_at']
    list_filter = ['status_code', 'network_code', 'created_at']
    search_fields = ['phone_number', 'message_id']
    readonly_fields = ['notification', 'phone_number', 'message_id', 'cost', 'status_code', 'network_code']
    ordering = ['-created_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'email_address', 'message_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['email_address', 'message_id']
    readonly_fields = ['notification', 'email_address', 'message_id', 'bounce_reason']
    ordering = ['-created_at']


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'platform', 'message_id', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['device_token', 'message_id']
    readonly_fields = ['notification', 'device_token', 'platform', 'message_id']
    ordering = ['-created_at']
