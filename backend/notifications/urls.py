from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NotificationTemplateViewSet, NotificationViewSet,
    UserNotificationSettingsViewSet, SMSLogViewSet,
    EmailLogViewSet, PushNotificationLogViewSet
)

router = DefaultRouter()
router.register(r'templates', NotificationTemplateViewSet, basename='notification-templates')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'settings', UserNotificationSettingsViewSet, basename='notification-settings')
router.register(r'sms-logs', SMSLogViewSet, basename='sms-logs')
router.register(r'email-logs', EmailLogViewSet, basename='email-logs')
router.register(r'push-logs', PushNotificationLogViewSet, basename='push-logs')

urlpatterns = [
    path('', include(router.urls)),
]