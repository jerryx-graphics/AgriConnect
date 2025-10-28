from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from core.permissions import IsOwnerOrReadOnly, IsTransporterOrReadOnly
from .models import (
    Vehicle, TransportCompany, DeliveryRoute, Delivery, DeliveryTracking,
    DeliveryZone, RouteOptimization, DeliveryFeedback
)
from .serializers import (
    VehicleSerializer, TransportCompanySerializer, DeliveryRouteSerializer,
    DeliverySerializer, DeliveryCreateSerializer, DeliveryTrackingSerializer,
    DeliveryZoneSerializer, RouteOptimizationSerializer, RouteOptimizationCreateSerializer,
    DeliveryFeedbackSerializer, DeliveryCostCalculationSerializer,
    TransporterSearchSerializer, DeliveryStatusUpdateSerializer, RouteCreationSerializer
)
from .services import LogisticsService, RouteOptimizationService, DeliveryAnalyticsService


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for vehicles"""
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle_type', 'fuel_type', 'is_active', 'is_available']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return Vehicle.objects.all()
        elif user.role == 'TRANSPORTER':
            return Vehicle.objects.filter(owner=user)
        else:
            return Vehicle.objects.filter(is_active=True, is_available=True)


class TransportCompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for transport companies"""
    serializer_class = TransportCompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_verified', 'is_active', 'is_accepting_orders']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return TransportCompany.objects.all()
        elif user.role == 'TRANSPORTER':
            return TransportCompany.objects.filter(owner=user)
        else:
            return TransportCompany.objects.filter(is_active=True, is_accepting_orders=True)


class DeliveryRouteViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery routes"""
    serializer_class = DeliveryRouteSerializer
    permission_classes = [IsAuthenticated, IsTransporterOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transporter', 'vehicle', 'is_active']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return DeliveryRoute.objects.all()
        elif user.role == 'TRANSPORTER':
            return DeliveryRoute.objects.filter(transporter=user)
        else:
            return DeliveryRoute.objects.filter(is_active=True)


class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for deliveries"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'transporter', 'is_paid']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return Delivery.objects.all()
        elif user.role == 'TRANSPORTER':
            return Delivery.objects.filter(transporter=user)
        elif user.role == 'BUYER':
            return Delivery.objects.filter(order__buyer=user)
        elif user.role == 'FARMER':
            return Delivery.objects.filter(order__items__product__farmer=user)
        else:
            return Delivery.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryCreateSerializer
        return DeliverySerializer

    def perform_create(self, serializer):
        delivery_data = serializer.validated_data
        order = delivery_data['order']

        # Create delivery using logistics service
        logistics_service = LogisticsService()
        delivery = logistics_service.create_delivery(
            order=order,
            transporter_id=delivery_data['transporter'].id,
            vehicle_id=delivery_data['vehicle'].id,
            delivery_data={
                'pickup_location': delivery_data['pickup_location'],
                'pickup_coordinates': delivery_data['pickup_coordinates'],
                'pickup_contact_name': delivery_data['pickup_contact_name'],
                'pickup_contact_phone': delivery_data['pickup_contact_phone'],
                'pickup_instructions': delivery_data.get('pickup_instructions', ''),
                'delivery_location': delivery_data['delivery_location'],
                'delivery_coordinates': delivery_data['delivery_coordinates'],
                'delivery_contact_name': delivery_data['delivery_contact_name'],
                'delivery_contact_phone': delivery_data['delivery_contact_phone'],
                'delivery_instructions': delivery_data.get('delivery_instructions', ''),
                'scheduled_pickup_time': delivery_data['scheduled_pickup_time'],
                'scheduled_delivery_time': delivery_data['scheduled_delivery_time'],
                'priority': delivery_data.get('priority', 'normal'),
                'total_weight_kg': delivery_data['total_weight_kg'],
                'total_volume_m3': delivery_data.get('total_volume_m3'),
                'package_count': delivery_data.get('package_count', 1),
                'special_handling': delivery_data.get('special_handling', [])
            }
        )

        return delivery

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get delivery tracking information"""
        delivery = self.get_object()
        logistics_service = LogisticsService()

        tracking_data = logistics_service.get_delivery_tracking(str(delivery.delivery_id))

        return Response(tracking_data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update delivery status"""
        delivery = self.get_object()

        # Check permission - only transporter or admin can update
        if request.user != delivery.transporter and request.user.role not in ['ADMIN', 'COOPERATIVE']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DeliveryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logistics_service = LogisticsService()
        tracking = logistics_service.update_delivery_status(
            delivery_id=str(delivery.delivery_id),
            status=serializer.validated_data['status'],
            location=serializer.validated_data['location'],
            coordinates=serializer.validated_data['coordinates'],
            notes=serializer.validated_data.get('notes'),
            updated_by_id=request.user.id
        )

        tracking_serializer = DeliveryTrackingSerializer(tracking)
        return Response(tracking_serializer.data)


class DeliveryTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for delivery tracking"""
    serializer_class = DeliveryTrackingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['delivery', 'is_automated']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return DeliveryTracking.objects.all()
        elif user.role == 'TRANSPORTER':
            return DeliveryTracking.objects.filter(delivery__transporter=user)
        elif user.role == 'BUYER':
            return DeliveryTracking.objects.filter(delivery__order__buyer=user)
        elif user.role == 'FARMER':
            return DeliveryTracking.objects.filter(delivery__order__items__product__farmer=user)
        else:
            return DeliveryTracking.objects.none()


class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for delivery zones"""
    queryset = DeliveryZone.objects.filter(is_active=True)
    serializer_class = DeliveryZoneSerializer
    permission_classes = [IsAuthenticated]


class RouteOptimizationViewSet(viewsets.ModelViewSet):
    """ViewSet for route optimization"""
    permission_classes = [IsAuthenticated, IsTransporterOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['optimization_type', 'algorithm', 'is_processed', 'is_used']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return RouteOptimization.objects.all()
        elif user.role == 'TRANSPORTER':
            return RouteOptimization.objects.filter(transporter=user)
        else:
            return RouteOptimization.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return RouteOptimizationCreateSerializer
        return RouteOptimizationSerializer

    def perform_create(self, serializer):
        optimization_request = serializer.validated_data
        optimization_request['transporter_id'] = self.request.user.id

        # Run optimization using service
        route_service = RouteOptimizationService()
        optimization = route_service.optimize_route(optimization_request)

        return optimization

    @action(detail=True, methods=['post'])
    def create_route(self, request, pk=None):
        """Create a delivery route from optimization results"""
        optimization = self.get_object()

        serializer = RouteCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        route_service = RouteOptimizationService()
        route = route_service.create_route_from_optimization(
            optimization_id=str(optimization.optimization_id),
            route_name=serializer.validated_data['route_name']
        )

        route_serializer = DeliveryRouteSerializer(route)
        return Response(route_serializer.data, status=status.HTTP_201_CREATED)


class DeliveryFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery feedback"""
    serializer_class = DeliveryFeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['delivery', 'overall_rating', 'damage_reported', 'is_resolved']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return DeliveryFeedback.objects.all()
        elif user.role == 'TRANSPORTER':
            return DeliveryFeedback.objects.filter(delivery__transporter=user)
        else:
            return DeliveryFeedback.objects.filter(customer=user)


class LogisticsAPIViewSet(viewsets.ViewSet):
    """General logistics API endpoints"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def calculate_cost(self, request):
        """Calculate delivery cost"""
        serializer = DeliveryCostCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logistics_service = LogisticsService()
        cost_info = logistics_service.calculate_delivery_cost(
            pickup_coords=serializer.validated_data['pickup_coordinates'],
            delivery_coords=serializer.validated_data['delivery_coordinates'],
            weight_kg=float(serializer.validated_data['weight_kg']),
            volume_m3=float(serializer.validated_data.get('volume_m3', 0)),
            priority=serializer.validated_data.get('priority', 'normal')
        )

        return Response(cost_info)

    @action(detail=False, methods=['post'])
    def find_transporters(self, request):
        """Find available transporters"""
        serializer = TransporterSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logistics_service = LogisticsService()
        transporters = logistics_service.find_available_transporters(
            pickup_coords=serializer.validated_data['pickup_coordinates'],
            delivery_coords=serializer.validated_data['delivery_coordinates'],
            weight_kg=float(serializer.validated_data['weight_kg']),
            delivery_date=serializer.validated_data['delivery_date'],
            max_distance_km=float(serializer.validated_data.get('max_distance_km', 50))
        )

        return Response({
            'available_transporters': transporters,
            'total_found': len(transporters)
        })

    @action(detail=False, methods=['get'])
    def transporter_performance(self, request):
        """Get transporter performance metrics"""
        if request.user.role not in ['TRANSPORTER', 'ADMIN', 'COOPERATIVE']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        transporter_id = request.user.id if request.user.role == 'TRANSPORTER' else request.query_params.get('transporter_id')

        if not transporter_id:
            return Response(
                {'error': 'Transporter ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        analytics_service = DeliveryAnalyticsService()
        performance = analytics_service.get_transporter_performance(int(transporter_id))

        return Response(performance)

    @action(detail=False, methods=['get'])
    def zone_analytics(self, request):
        """Get delivery zone analytics"""
        zone_id = request.query_params.get('zone_id')

        if not zone_id:
            return Response(
                {'error': 'Zone ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        analytics_service = DeliveryAnalyticsService()
        analytics = analytics_service.get_delivery_zone_analytics(int(zone_id))

        return Response(analytics)
