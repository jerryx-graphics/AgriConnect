from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import (
    Notification, NotificationTemplate, UserNotificationSettings,
    SMSLog, EmailLog, PushNotificationLog
)
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    UserNotificationSettingsSerializer, SMSLogSerializer,
    EmailLogSerializer, PushNotificationLogSerializer,
    SendNotificationSerializer, BulkNotificationSerializer,
    MarkAsReadSerializer
)
from .services import NotificationService

User = get_user_model()


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification templates"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'channel', 'is_active']
    search_fields = ['name', 'message_template']
    ordering_fields = ['name', 'notification_type', 'channel', 'created_at']
    ordering = ['notification_type', 'channel']


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'channel', 'template__notification_type']
    ordering_fields = ['created_at', 'sent_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return notifications for the current user"""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('template', 'recipient')

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark notifications as read"""
        serializer = MarkAsReadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data['notification_ids']
        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            channel='IN_APP'
        ).update(status='READ', read_at=timezone.now())

        return Response({
            'message': f'Marked {updated_count} notifications as read',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread in-app notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            channel='IN_APP',
            status__in=['PENDING', 'SENT']
        ).count()

        return Response({'unread_count': count})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_custom(self, request):
        """Send custom notification to specific users"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can send custom notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient_ids = serializer.validated_data['recipient_ids']
        notification_type = serializer.validated_data['notification_type']
        channels = serializer.validated_data.get('channels', None)
        context_data = serializer.validated_data.get('context_data', {})

        sent_notifications = []
        for user_id in recipient_ids:
            try:
                user = User.objects.get(id=user_id)
                notifications = NotificationService.send_notification(
                    user=user,
                    notification_type=notification_type,
                    context_data=context_data,
                    channels=channels
                )
                sent_notifications.extend(notifications)
            except User.DoesNotExist:
                continue

        return Response({
            'message': f'Sent {len(sent_notifications)} notifications',
            'notification_count': len(sent_notifications)
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_bulk(self, request):
        """Send bulk notification to user groups"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can send bulk notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = BulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient_type = serializer.validated_data['recipient_type']
        notification_type = serializer.validated_data['notification_type']
        channels = serializer.validated_data.get('channels', None)
        context_data = serializer.validated_data.get('context_data', {})

        # Get users based on recipient type
        if recipient_type == 'ALL_USERS':
            users = User.objects.filter(is_active=True)
        elif recipient_type == 'FARMERS':
            users = User.objects.filter(role='FARMER', is_active=True)
        elif recipient_type == 'BUYERS':
            users = User.objects.filter(role='BUYER', is_active=True)
        elif recipient_type == 'TRANSPORTERS':
            users = User.objects.filter(role='TRANSPORTER', is_active=True)
        elif recipient_type == 'COOPERATIVES':
            users = User.objects.filter(role='COOPERATIVE', is_active=True)
        else:
            users = User.objects.none()

        sent_notifications = []
        for user in users:
            notifications = NotificationService.send_notification(
                user=user,
                notification_type=notification_type,
                context_data=context_data,
                channels=channels
            )
            sent_notifications.extend(notifications)

        return Response({
            'message': f'Sent notifications to {users.count()} users',
            'user_count': users.count(),
            'notification_count': len(sent_notifications)
        })


class UserNotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user notification settings"""
    serializer_class = UserNotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return settings for the current user"""
        if self.request.user.is_staff:
            return UserNotificationSettings.objects.all()
        return UserNotificationSettings.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create settings for the current user"""
        if 'pk' in self.kwargs:
            return super().get_object()

        # For current user's settings
        settings, created = UserNotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings

    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_settings(self, request):
        """Get or update current user's notification settings"""
        settings, created = UserNotificationSettings.objects.get_or_create(
            user=request.user
        )

        if request.method == 'GET':
            serializer = self.get_serializer(settings)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(settings, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class SMSLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing SMS logs"""
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status_code', 'network_code']
    ordering_fields = ['created_at', 'cost']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return SMS logs for the current user's notifications"""
        if self.request.user.is_staff:
            return SMSLog.objects.all().select_related('notification__template')

        return SMSLog.objects.filter(
            notification__recipient=self.request.user
        ).select_related('notification__template')


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing email logs"""
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return email logs for the current user's notifications"""
        if self.request.user.is_staff:
            return EmailLog.objects.all().select_related('notification__template')

        return EmailLog.objects.filter(
            notification__recipient=self.request.user
        ).select_related('notification__template')


class PushNotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing push notification logs"""
    serializer_class = PushNotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['platform']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return push notification logs for the current user's notifications"""
        if self.request.user.is_staff:
            return PushNotificationLog.objects.all().select_related('notification__template')

        return PushNotificationLog.objects.filter(
            notification__recipient=self.request.user
        ).select_related('notification__template')
