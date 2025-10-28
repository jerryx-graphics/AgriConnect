from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import BaseModel
from orders.models import Order

User = get_user_model()


class Vehicle(BaseModel):
    """Vehicles used for transportation"""
    VEHICLE_TYPE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('trailer', 'Trailer'),
        ('bicycle', 'Bicycle'),
    ]

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('manual', 'Manual (Bicycle)'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)

    # Capacity and specifications
    max_weight_capacity = models.DecimalField(max_digits=8, decimal_places=2, help_text="Maximum weight in kg")
    max_volume_capacity = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Maximum volume in cubic meters")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    fuel_consumption = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fuel consumption per 100km")

    # Vehicle details
    color = models.CharField(max_length=30, null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    current_location = models.CharField(max_length=200, null=True, blank=True)
    current_coordinates = models.JSONField(default=dict, help_text="Current latitude and longitude")

    # Performance metrics
    total_distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    total_deliveries = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"


class TransportCompany(BaseModel):
    """Transport companies and logistics providers"""
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transport_companies')
    registration_number = models.CharField(max_length=50, unique=True)

    # Contact information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    operating_area = models.JSONField(default=list, help_text="List of areas/counties they operate in")

    # Business details
    license_number = models.CharField(max_length=50, null=True, blank=True)
    insurance_details = models.JSONField(default=dict)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0'))
    average_delivery_time = models.DurationField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_accepting_orders = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Transport Companies"

    def __str__(self):
        return self.name

    @property
    def success_rate(self):
        if self.total_deliveries > 0:
            return (self.successful_deliveries / self.total_deliveries) * 100
        return 0


class DeliveryRoute(BaseModel):
    """Optimized delivery routes"""
    route_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    transporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_routes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')

    # Route details
    start_location = models.CharField(max_length=200)
    start_coordinates = models.JSONField(default=dict)
    end_location = models.CharField(max_length=200)
    end_coordinates = models.JSONField(default=dict)

    # Waypoints and stops
    waypoints = models.JSONField(default=list, help_text="Intermediate stops with coordinates")
    total_distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_duration_minutes = models.PositiveIntegerField()

    # Route optimization
    optimization_algorithm = models.CharField(max_length=50, default='dijkstra')
    optimization_factors = models.JSONField(default=dict, help_text="Factors considered in optimization")
    traffic_data_used = models.BooleanField(default=False)

    # Status and usage
    is_active = models.BooleanField(default=True)
    times_used = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Route: {self.start_location} → {self.end_location}"


class Delivery(BaseModel):
    """Individual delivery records"""
    DELIVERY_STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    delivery_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    transporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='deliveries')
    route = models.ForeignKey(DeliveryRoute, on_delete=models.SET_NULL, null=True, blank=True)

    # Pickup details
    pickup_location = models.CharField(max_length=200)
    pickup_coordinates = models.JSONField(default=dict)
    pickup_contact_name = models.CharField(max_length=100)
    pickup_contact_phone = models.CharField(max_length=20)
    pickup_instructions = models.TextField(null=True, blank=True)

    # Delivery details
    delivery_location = models.CharField(max_length=200)
    delivery_coordinates = models.JSONField(default=dict)
    delivery_contact_name = models.CharField(max_length=100)
    delivery_contact_phone = models.CharField(max_length=20)
    delivery_instructions = models.TextField(null=True, blank=True)

    # Timing
    scheduled_pickup_time = models.DateTimeField()
    scheduled_delivery_time = models.DateTimeField()
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)

    # Status and priority
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='assigned')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    # Package details
    total_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    total_volume_m3 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    package_count = models.PositiveIntegerField(default=1)
    special_handling = models.JSONField(default=list, help_text="Special handling requirements")

    # Cost and payment
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    toll_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    # Performance tracking
    distance_traveled_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fuel_consumption = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Issues and notes
    delivery_notes = models.TextField(null=True, blank=True)
    issues_encountered = models.JSONField(default=list)
    customer_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    customer_feedback = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_delivery_time']
        verbose_name_plural = "Deliveries"

    def __str__(self):
        return f"Delivery {self.delivery_id} - {self.order.order_id}"


class DeliveryTracking(BaseModel):
    """Real-time tracking of deliveries"""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_updates')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200)
    coordinates = models.JSONField(default=dict, help_text="Current latitude and longitude")

    # Status and details
    status_update = models.CharField(max_length=100)
    notes = models.TextField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)

    # Environmental data
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Vehicle data
    speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fuel_level_percentage = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Automated vs manual update
    is_automated = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Tracking {self.delivery.delivery_id} at {self.timestamp}"


class DeliveryZone(BaseModel):
    """Delivery zones and coverage areas"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    # Geographic boundaries
    boundary_coordinates = models.JSONField(help_text="Polygon coordinates defining the zone boundary")
    center_coordinates = models.JSONField(default=dict, help_text="Center point of the zone")

    # Zone details
    coverage_area_km2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    population_estimate = models.PositiveIntegerField(null=True, blank=True)

    # Service availability
    is_active = models.BooleanField(default=True)
    service_days = models.JSONField(default=list, help_text="Days of the week when service is available")
    service_hours = models.JSONField(default=dict, help_text="Service hours for each day")

    # Delivery metrics
    base_delivery_cost = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_km = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Performance metrics
    average_delivery_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def success_rate(self):
        if self.total_deliveries > 0:
            return (self.successful_deliveries / self.total_deliveries) * 100
        return 0


class RouteOptimization(BaseModel):
    """Route optimization requests and results"""
    OPTIMIZATION_TYPE_CHOICES = [
        ('distance', 'Minimize Distance'),
        ('time', 'Minimize Time'),
        ('cost', 'Minimize Cost'),
        ('fuel', 'Minimize Fuel Consumption'),
        ('balanced', 'Balanced Optimization'),
    ]

    ALGORITHM_CHOICES = [
        ('dijkstra', 'Dijkstra Algorithm'),
        ('a_star', 'A* Algorithm'),
        ('genetic', 'Genetic Algorithm'),
        ('simulated_annealing', 'Simulated Annealing'),
        ('greedy', 'Greedy Algorithm'),
    ]

    optimization_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    transporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_optimizations')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='optimizations')

    # Optimization parameters
    optimization_type = models.CharField(max_length=20, choices=OPTIMIZATION_TYPE_CHOICES)
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES)

    # Input data
    start_location = models.JSONField(help_text="Starting point coordinates")
    end_location = models.JSONField(help_text="End point coordinates")
    waypoints = models.JSONField(default=list, help_text="Required waypoints")
    delivery_windows = models.JSONField(default=dict, help_text="Time windows for each delivery")

    # Constraints
    max_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    avoid_toll_roads = models.BooleanField(default=False)
    avoid_highways = models.BooleanField(default=False)

    # Results
    optimized_route = models.JSONField(default=dict, help_text="Optimized route with coordinates")
    total_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    estimated_fuel_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_toll_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Processing
    processing_time_seconds = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)

    # Usage
    is_used = models.BooleanField(default=False)
    created_route = models.ForeignKey(DeliveryRoute, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Optimization {self.optimization_id} - {self.optimization_type}"


class DeliveryFeedback(BaseModel):
    """Customer feedback on deliveries"""
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='feedback')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_feedback')

    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    condition_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Feedback
    comments = models.TextField(null=True, blank=True)
    improvement_suggestions = models.TextField(null=True, blank=True)

    # Issues
    issues_reported = models.JSONField(default=list, help_text="List of issues encountered")
    damage_reported = models.BooleanField(default=False)
    damage_description = models.TextField(null=True, blank=True)

    # Follow-up
    requires_follow_up = models.BooleanField(default=False)
    follow_up_notes = models.TextField(null=True, blank=True)
    is_resolved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for Delivery {self.delivery.delivery_id} - {self.overall_rating}/5"
