from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Vehicle, TransportCompany, DeliveryRoute, Delivery, DeliveryTracking,
    DeliveryZone, RouteOptimization, DeliveryFeedback
)
from orders.models import Order

User = get_user_model()


class VehicleSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'owner_name', 'vehicle_type', 'make', 'model', 'year',
            'license_plate', 'max_weight_capacity', 'max_volume_capacity',
            'fuel_type', 'fuel_consumption', 'color', 'insurance_expiry',
            'registration_expiry', 'is_active', 'is_available', 'current_location',
            'current_coordinates', 'total_distance_km', 'total_deliveries',
            'average_rating', 'created_at'
        ]
        read_only_fields = [
            'id', 'owner', 'owner_name', 'total_distance_km', 'total_deliveries',
            'average_rating', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TransportCompanySerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    success_rate = serializers.ReadOnlyField()

    class Meta:
        model = TransportCompany
        fields = [
            'id', 'name', 'owner', 'owner_name', 'registration_number',
            'phone', 'email', 'address', 'operating_area', 'license_number',
            'insurance_details', 'is_verified', 'verification_date',
            'total_deliveries', 'successful_deliveries', 'average_rating',
            'average_delivery_time', 'success_rate', 'is_active',
            'is_accepting_orders', 'created_at'
        ]
        read_only_fields = [
            'id', 'owner', 'owner_name', 'is_verified', 'verification_date',
            'total_deliveries', 'successful_deliveries', 'average_rating',
            'average_delivery_time', 'success_rate', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class DeliveryRouteSerializer(serializers.ModelSerializer):
    transporter_name = serializers.CharField(source='transporter.get_full_name', read_only=True)
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryRoute
        fields = [
            'route_id', 'name', 'transporter', 'transporter_name', 'vehicle',
            'vehicle_info', 'start_location', 'start_coordinates', 'end_location',
            'end_coordinates', 'waypoints', 'total_distance_km',
            'estimated_duration_minutes', 'optimization_algorithm',
            'optimization_factors', 'traffic_data_used', 'is_active',
            'times_used', 'last_used', 'created_at'
        ]
        read_only_fields = [
            'route_id', 'transporter', 'transporter_name', 'vehicle_info',
            'times_used', 'last_used', 'created_at'
        ]

    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.make} {obj.vehicle.model} ({obj.vehicle.license_plate})"

    def create(self, validated_data):
        validated_data['transporter'] = self.context['request'].user
        return super().create(validated_data)


class DeliveryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            'order', 'transporter', 'vehicle', 'pickup_location', 'pickup_coordinates',
            'pickup_contact_name', 'pickup_contact_phone', 'pickup_instructions',
            'delivery_location', 'delivery_coordinates', 'delivery_contact_name',
            'delivery_contact_phone', 'delivery_instructions', 'scheduled_pickup_time',
            'scheduled_delivery_time', 'priority', 'total_weight_kg',
            'total_volume_m3', 'package_count', 'special_handling'
        ]


class DeliverySerializer(serializers.ModelSerializer):
    order_info = serializers.SerializerMethodField()
    transporter_name = serializers.CharField(source='transporter.get_full_name', read_only=True)
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            'delivery_id', 'order', 'order_info', 'transporter', 'transporter_name',
            'vehicle', 'vehicle_info', 'pickup_location', 'pickup_coordinates',
            'pickup_contact_name', 'pickup_contact_phone', 'pickup_instructions',
            'delivery_location', 'delivery_coordinates', 'delivery_contact_name',
            'delivery_contact_phone', 'delivery_instructions', 'scheduled_pickup_time',
            'scheduled_delivery_time', 'actual_pickup_time', 'actual_delivery_time',
            'status', 'priority', 'total_weight_kg', 'total_volume_m3',
            'package_count', 'special_handling', 'delivery_cost', 'fuel_cost',
            'toll_cost', 'is_paid', 'distance_traveled_km', 'fuel_consumption',
            'delivery_notes', 'issues_encountered', 'customer_rating',
            'customer_feedback', 'created_at'
        ]
        read_only_fields = [
            'delivery_id', 'order_info', 'transporter_name', 'vehicle_info',
            'actual_pickup_time', 'actual_delivery_time', 'delivery_cost',
            'fuel_cost', 'toll_cost', 'distance_traveled_km', 'fuel_consumption',
            'created_at'
        ]

    def get_order_info(self, obj):
        return {
            'order_id': obj.order.order_id,
            'total_amount': float(obj.order.total_amount),
            'buyer_name': obj.order.buyer.get_full_name()
        }

    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.make} {obj.vehicle.model} ({obj.vehicle.license_plate})"


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)

    class Meta:
        model = DeliveryTracking
        fields = [
            'id', 'delivery', 'timestamp', 'location', 'coordinates',
            'status_update', 'notes', 'estimated_arrival', 'temperature',
            'humidity', 'speed_kmh', 'fuel_level_percentage', 'is_automated',
            'updated_by', 'updated_by_name'
        ]
        read_only_fields = ['id', 'timestamp', 'updated_by_name']


class DeliveryZoneSerializer(serializers.ModelSerializer):
    success_rate = serializers.ReadOnlyField()

    class Meta:
        model = DeliveryZone
        fields = [
            'id', 'name', 'description', 'boundary_coordinates', 'center_coordinates',
            'coverage_area_km2', 'population_estimate', 'is_active', 'service_days',
            'service_hours', 'base_delivery_cost', 'cost_per_km', 'minimum_order_value',
            'average_delivery_time_minutes', 'total_deliveries', 'successful_deliveries',
            'success_rate', 'created_at'
        ]
        read_only_fields = [
            'id', 'average_delivery_time_minutes', 'total_deliveries',
            'successful_deliveries', 'success_rate', 'created_at'
        ]


class RouteOptimizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteOptimization
        fields = [
            'vehicle', 'optimization_type', 'algorithm', 'start_location',
            'end_location', 'waypoints', 'delivery_windows', 'max_distance_km',
            'max_duration_minutes', 'avoid_toll_roads', 'avoid_highways'
        ]

    def create(self, validated_data):
        validated_data['transporter'] = self.context['request'].user
        return super().create(validated_data)


class RouteOptimizationSerializer(serializers.ModelSerializer):
    transporter_name = serializers.CharField(source='transporter.get_full_name', read_only=True)
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = RouteOptimization
        fields = [
            'optimization_id', 'transporter', 'transporter_name', 'vehicle',
            'vehicle_info', 'optimization_type', 'algorithm', 'start_location',
            'end_location', 'waypoints', 'delivery_windows', 'max_distance_km',
            'max_duration_minutes', 'avoid_toll_roads', 'avoid_highways',
            'optimized_route', 'total_distance_km', 'total_duration_minutes',
            'estimated_fuel_cost', 'estimated_toll_cost', 'processing_time_seconds',
            'is_processed', 'processing_error', 'is_used', 'created_route',
            'created_at'
        ]
        read_only_fields = [
            'optimization_id', 'transporter', 'transporter_name', 'vehicle_info',
            'optimized_route', 'total_distance_km', 'total_duration_minutes',
            'estimated_fuel_cost', 'estimated_toll_cost', 'processing_time_seconds',
            'is_processed', 'processing_error', 'is_used', 'created_route',
            'created_at'
        ]

    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.make} {obj.vehicle.model} ({obj.vehicle.license_plate})"


class DeliveryFeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    delivery_info = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryFeedback
        fields = [
            'id', 'delivery', 'delivery_info', 'customer', 'customer_name',
            'overall_rating', 'timeliness_rating', 'condition_rating',
            'service_rating', 'comments', 'improvement_suggestions',
            'issues_reported', 'damage_reported', 'damage_description',
            'requires_follow_up', 'follow_up_notes', 'is_resolved',
            'created_at'
        ]
        read_only_fields = ['id', 'delivery_info', 'customer_name', 'created_at']

    def get_delivery_info(self, obj):
        return {
            'delivery_id': str(obj.delivery.delivery_id),
            'order_id': obj.delivery.order.order_id,
            'status': obj.delivery.status
        }

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


class DeliveryCostCalculationSerializer(serializers.Serializer):
    pickup_coordinates = serializers.JSONField()
    delivery_coordinates = serializers.JSONField()
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    volume_m3 = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high', 'urgent'],
        default='normal'
    )


class TransporterSearchSerializer(serializers.Serializer):
    pickup_coordinates = serializers.JSONField()
    delivery_coordinates = serializers.JSONField()
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    delivery_date = serializers.DateTimeField()
    max_distance_km = serializers.DecimalField(max_digits=8, decimal_places=2, default=50)


class DeliveryStatusUpdateSerializer(serializers.Serializer):
    delivery_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=[
        'assigned', 'picked_up', 'in_transit', 'out_for_delivery',
        'delivered', 'failed', 'returned', 'cancelled'
    ])
    location = serializers.CharField(max_length=200)
    coordinates = serializers.JSONField()
    notes = serializers.CharField(max_length=500, required=False)


class RouteCreationSerializer(serializers.Serializer):
    optimization_id = serializers.UUIDField()
    route_name = serializers.CharField(max_length=100)