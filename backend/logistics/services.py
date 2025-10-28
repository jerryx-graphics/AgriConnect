from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Avg, Count, F, Sum
# from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import Distance
import math
import heapq
from datetime import datetime, timedelta
import logging

from .models import (
    Vehicle, TransportCompany, DeliveryRoute, Delivery, DeliveryTracking,
    DeliveryZone, RouteOptimization, DeliveryFeedback
)
from orders.models import Order
from users.models import User

logger = logging.getLogger(__name__)


class LogisticsService:
    """Main service for logistics operations"""

    def calculate_delivery_cost(self, pickup_coords: Dict, delivery_coords: Dict,
                              weight_kg: float, volume_m3: Optional[float] = None,
                              priority: str = 'normal') -> Dict[str, Any]:
        """Calculate delivery cost based on distance, weight, and priority"""

        # Calculate distance using Haversine formula
        distance_km = self._calculate_distance(pickup_coords, delivery_coords)

        # Base cost calculation
        base_cost = Decimal('50.00')  # Base delivery fee in KSH
        distance_cost = Decimal(str(distance_km)) * Decimal('15.00')  # KSH per km
        weight_cost = Decimal(str(weight_kg)) * Decimal('5.00')  # KSH per kg

        # Volume surcharge if provided
        volume_cost = Decimal('0')
        if volume_m3:
            volume_cost = Decimal(str(volume_m3)) * Decimal('20.00')  # KSH per cubic meter

        # Priority surcharge
        priority_multiplier = {
            'low': Decimal('0.8'),
            'normal': Decimal('1.0'),
            'high': Decimal('1.3'),
            'urgent': Decimal('1.8')
        }

        total_cost = (base_cost + distance_cost + weight_cost + volume_cost) * priority_multiplier.get(priority, Decimal('1.0'))

        return {
            'base_cost': float(base_cost),
            'distance_cost': float(distance_cost),
            'weight_cost': float(weight_cost),
            'volume_cost': float(volume_cost),
            'priority_multiplier': float(priority_multiplier.get(priority, Decimal('1.0'))),
            'total_cost': float(total_cost),
            'distance_km': distance_km,
            'estimated_duration_minutes': int(distance_km * 2)  # Rough estimate: 2 minutes per km
        }

    def find_available_transporters(self, pickup_coords: Dict, delivery_coords: Dict,
                                  weight_kg: float, delivery_date: datetime,
                                  max_distance_km: float = 50) -> List[Dict]:
        """Find available transporters for a delivery"""

        # Find vehicles that can handle the weight
        suitable_vehicles = Vehicle.objects.filter(
            is_active=True,
            is_available=True,
            max_weight_capacity__gte=weight_kg,
            owner__role='TRANSPORTER'
        ).select_related('owner')

        available_transporters = []

        for vehicle in suitable_vehicles:
            # Calculate distance from vehicle's current location to pickup
            if vehicle.current_coordinates:
                distance_to_pickup = self._calculate_distance(
                    vehicle.current_coordinates, pickup_coords
                )

                if distance_to_pickup <= max_distance_km:
                    # Check if transporter is available at delivery_date
                    # (This would check their schedule in a real implementation)

                    delivery_distance = self._calculate_distance(pickup_coords, delivery_coords)
                    cost_estimate = self.calculate_delivery_cost(
                        pickup_coords, delivery_coords, weight_kg
                    )

                    available_transporters.append({
                        'transporter_id': vehicle.owner.id,
                        'transporter_name': vehicle.owner.get_full_name(),
                        'vehicle_id': vehicle.id,
                        'vehicle_info': f"{vehicle.make} {vehicle.model} ({vehicle.license_plate})",
                        'vehicle_type': vehicle.vehicle_type,
                        'capacity_kg': float(vehicle.max_weight_capacity),
                        'rating': float(vehicle.average_rating),
                        'distance_to_pickup_km': distance_to_pickup,
                        'estimated_cost': cost_estimate['total_cost'],
                        'estimated_duration_minutes': cost_estimate['estimated_duration_minutes']
                    })

        # Sort by rating and distance
        available_transporters.sort(key=lambda x: (-x['rating'], x['distance_to_pickup_km']))

        return available_transporters

    def create_delivery(self, order: Order, transporter_id: int, vehicle_id: int,
                       delivery_data: Dict) -> Delivery:
        """Create a new delivery assignment"""

        transporter = User.objects.get(id=transporter_id, role='TRANSPORTER')
        vehicle = Vehicle.objects.get(id=vehicle_id, owner=transporter)

        # Calculate costs
        cost_info = self.calculate_delivery_cost(
            delivery_data['pickup_coordinates'],
            delivery_data['delivery_coordinates'],
            delivery_data['total_weight_kg'],
            delivery_data.get('total_volume_m3'),
            delivery_data.get('priority', 'normal')
        )

        delivery = Delivery.objects.create(
            order=order,
            transporter=transporter,
            vehicle=vehicle,
            pickup_location=delivery_data['pickup_location'],
            pickup_coordinates=delivery_data['pickup_coordinates'],
            pickup_contact_name=delivery_data['pickup_contact_name'],
            pickup_contact_phone=delivery_data['pickup_contact_phone'],
            pickup_instructions=delivery_data.get('pickup_instructions', ''),
            delivery_location=delivery_data['delivery_location'],
            delivery_coordinates=delivery_data['delivery_coordinates'],
            delivery_contact_name=delivery_data['delivery_contact_name'],
            delivery_contact_phone=delivery_data['delivery_contact_phone'],
            delivery_instructions=delivery_data.get('delivery_instructions', ''),
            scheduled_pickup_time=delivery_data['scheduled_pickup_time'],
            scheduled_delivery_time=delivery_data['scheduled_delivery_time'],
            priority=delivery_data.get('priority', 'normal'),
            total_weight_kg=delivery_data['total_weight_kg'],
            total_volume_m3=delivery_data.get('total_volume_m3'),
            package_count=delivery_data.get('package_count', 1),
            special_handling=delivery_data.get('special_handling', []),
            delivery_cost=cost_info['total_cost']
        )

        # Create initial tracking entry
        DeliveryTracking.objects.create(
            delivery=delivery,
            location=delivery_data['pickup_location'],
            coordinates=delivery_data['pickup_coordinates'],
            status_update="Delivery assigned to transporter",
            estimated_arrival=delivery_data['scheduled_pickup_time']
        )

        # Update order status
        order.status = 'processing'
        order.save()

        return delivery

    def update_delivery_status(self, delivery_id: str, status: str,
                             location: str, coordinates: Dict,
                             notes: str = None, updated_by_id: int = None) -> DeliveryTracking:
        """Update delivery status and create tracking entry"""

        delivery = Delivery.objects.get(delivery_id=delivery_id)
        delivery.status = status

        # Update timestamps based on status
        if status == 'picked_up' and not delivery.actual_pickup_time:
            delivery.actual_pickup_time = timezone.now()
        elif status == 'delivered' and not delivery.actual_delivery_time:
            delivery.actual_delivery_time = timezone.now()

        delivery.save()

        # Create tracking entry
        tracking = DeliveryTracking.objects.create(
            delivery=delivery,
            location=location,
            coordinates=coordinates,
            status_update=f"Status updated to: {status}",
            notes=notes,
            updated_by_id=updated_by_id,
            is_automated=updated_by_id is None
        )

        # Update order status if delivered
        if status == 'delivered':
            delivery.order.status = 'delivered'
            delivery.order.save()

        return tracking

    def get_delivery_tracking(self, delivery_id: str) -> Dict[str, Any]:
        """Get complete tracking information for a delivery"""

        try:
            delivery = Delivery.objects.select_related(
                'order', 'transporter', 'vehicle'
            ).get(delivery_id=delivery_id)

            tracking_updates = delivery.tracking_updates.order_by('timestamp')

            return {
                'delivery_id': str(delivery.delivery_id),
                'order_id': delivery.order.order_id,
                'status': delivery.status,
                'transporter': {
                    'name': delivery.transporter.get_full_name(),
                    'phone': delivery.transporter.phone,
                    'rating': float(delivery.vehicle.average_rating)
                },
                'vehicle': {
                    'info': f"{delivery.vehicle.make} {delivery.vehicle.model}",
                    'license_plate': delivery.vehicle.license_plate,
                    'type': delivery.vehicle.vehicle_type
                },
                'pickup': {
                    'location': delivery.pickup_location,
                    'coordinates': delivery.pickup_coordinates,
                    'contact': delivery.pickup_contact_name,
                    'phone': delivery.pickup_contact_phone,
                    'scheduled_time': delivery.scheduled_pickup_time,
                    'actual_time': delivery.actual_pickup_time
                },
                'delivery': {
                    'location': delivery.delivery_location,
                    'coordinates': delivery.delivery_coordinates,
                    'contact': delivery.delivery_contact_name,
                    'phone': delivery.delivery_contact_phone,
                    'scheduled_time': delivery.scheduled_delivery_time,
                    'actual_time': delivery.actual_delivery_time
                },
                'tracking_updates': [
                    {
                        'timestamp': update.timestamp,
                        'location': update.location,
                        'coordinates': update.coordinates,
                        'status': update.status_update,
                        'notes': update.notes,
                        'estimated_arrival': update.estimated_arrival
                    }
                    for update in tracking_updates
                ],
                'cost': float(delivery.delivery_cost),
                'priority': delivery.priority
            }

        except Delivery.DoesNotExist:
            return {'error': 'Delivery not found'}

    def _calculate_distance(self, coord1: Dict, coord2: Dict) -> float:
        """Calculate distance between two coordinates using Haversine formula"""

        lat1, lon1 = coord1.get('latitude', 0), coord1.get('longitude', 0)
        lat2, lon2 = coord2.get('latitude', 0), coord2.get('longitude', 0)

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in km
        r = 6371

        return r * c


class RouteOptimizationService:
    """Service for route optimization and planning"""

    def optimize_route(self, optimization_request: Dict) -> RouteOptimization:
        """Optimize delivery route using specified algorithm"""

        transporter = User.objects.get(id=optimization_request['transporter_id'])
        vehicle = Vehicle.objects.get(id=optimization_request['vehicle_id'])

        route_opt = RouteOptimization.objects.create(
            transporter=transporter,
            vehicle=vehicle,
            optimization_type=optimization_request['optimization_type'],
            algorithm=optimization_request.get('algorithm', 'dijkstra'),
            start_location=optimization_request['start_location'],
            end_location=optimization_request['end_location'],
            waypoints=optimization_request.get('waypoints', []),
            delivery_windows=optimization_request.get('delivery_windows', {}),
            max_distance_km=optimization_request.get('max_distance_km'),
            max_duration_minutes=optimization_request.get('max_duration_minutes'),
            avoid_toll_roads=optimization_request.get('avoid_toll_roads', False),
            avoid_highways=optimization_request.get('avoid_highways', False)
        )

        # Run optimization algorithm
        start_time = timezone.now()

        try:
            if route_opt.algorithm == 'dijkstra':
                result = self._dijkstra_optimization(route_opt)
            elif route_opt.algorithm == 'greedy':
                result = self._greedy_optimization(route_opt)
            else:
                result = self._basic_optimization(route_opt)

            processing_time = (timezone.now() - start_time).total_seconds()

            route_opt.optimized_route = result['route']
            route_opt.total_distance_km = result['distance']
            route_opt.total_duration_minutes = result['duration']
            route_opt.estimated_fuel_cost = result['fuel_cost']
            route_opt.processing_time_seconds = processing_time
            route_opt.is_processed = True

        except Exception as e:
            route_opt.processing_error = str(e)
            logger.error(f"Route optimization failed: {e}")

        route_opt.save()
        return route_opt

    def create_route_from_optimization(self, optimization_id: str, route_name: str) -> DeliveryRoute:
        """Create a delivery route from optimization results"""

        optimization = RouteOptimization.objects.get(optimization_id=optimization_id)

        if not optimization.is_processed or not optimization.optimized_route:
            raise ValueError("Optimization not completed or failed")

        route = DeliveryRoute.objects.create(
            name=route_name,
            transporter=optimization.transporter,
            vehicle=optimization.vehicle,
            start_location=optimization.optimized_route.get('start_address', ''),
            start_coordinates=optimization.start_location,
            end_location=optimization.optimized_route.get('end_address', ''),
            end_coordinates=optimization.end_location,
            waypoints=optimization.optimized_route.get('waypoints', []),
            total_distance_km=optimization.total_distance_km,
            estimated_duration_minutes=optimization.total_duration_minutes,
            optimization_algorithm=optimization.algorithm,
            optimization_factors={
                'type': optimization.optimization_type,
                'avoid_tolls': optimization.avoid_toll_roads,
                'avoid_highways': optimization.avoid_highways
            }
        )

        optimization.created_route = route
        optimization.is_used = True
        optimization.save()

        return route

    def _dijkstra_optimization(self, route_opt: RouteOptimization) -> Dict:
        """Dijkstra-based route optimization"""

        # Simplified implementation - in production would use proper graph algorithms
        waypoints = route_opt.waypoints
        start = route_opt.start_location
        end = route_opt.end_location

        # Create simple route through all waypoints
        all_points = [start] + waypoints + [end]
        total_distance = 0
        optimized_waypoints = []

        for i in range(len(all_points) - 1):
            distance = self._calculate_distance_between_points(all_points[i], all_points[i + 1])
            total_distance += distance
            optimized_waypoints.append(all_points[i + 1])

        duration = int(total_distance * 2)  # 2 minutes per km estimate
        fuel_cost = total_distance * 12  # KSH 12 per km fuel cost

        return {
            'route': {
                'waypoints': optimized_waypoints,
                'total_points': len(all_points),
                'algorithm_used': 'dijkstra'
            },
            'distance': total_distance,
            'duration': duration,
            'fuel_cost': fuel_cost
        }

    def _greedy_optimization(self, route_opt: RouteOptimization) -> Dict:
        """Greedy nearest-neighbor optimization"""

        waypoints = route_opt.waypoints[:]
        start = route_opt.start_location
        end = route_opt.end_location

        # Greedy nearest neighbor
        current_point = start
        optimized_route = [current_point]
        total_distance = 0

        while waypoints:
            nearest_idx = 0
            nearest_distance = float('inf')

            for i, waypoint in enumerate(waypoints):
                distance = self._calculate_distance_between_points(current_point, waypoint)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_idx = i

            # Move to nearest waypoint
            next_point = waypoints.pop(nearest_idx)
            optimized_route.append(next_point)
            total_distance += nearest_distance
            current_point = next_point

        # Add final distance to end
        final_distance = self._calculate_distance_between_points(current_point, end)
        total_distance += final_distance
        optimized_route.append(end)

        duration = int(total_distance * 2)
        fuel_cost = total_distance * 12

        return {
            'route': {
                'waypoints': optimized_route[1:-1],  # Exclude start and end
                'total_points': len(optimized_route),
                'algorithm_used': 'greedy'
            },
            'distance': total_distance,
            'duration': duration,
            'fuel_cost': fuel_cost
        }

    def _basic_optimization(self, route_opt: RouteOptimization) -> Dict:
        """Basic optimization - just connects points in order"""

        waypoints = route_opt.waypoints
        start = route_opt.start_location
        end = route_opt.end_location

        all_points = [start] + waypoints + [end]
        total_distance = 0

        for i in range(len(all_points) - 1):
            distance = self._calculate_distance_between_points(all_points[i], all_points[i + 1])
            total_distance += distance

        duration = int(total_distance * 2)
        fuel_cost = total_distance * 12

        return {
            'route': {
                'waypoints': waypoints,
                'total_points': len(all_points),
                'algorithm_used': 'basic'
            },
            'distance': total_distance,
            'duration': duration,
            'fuel_cost': fuel_cost
        }

    def _calculate_distance_between_points(self, point1: Dict, point2: Dict) -> float:
        """Calculate distance between two coordinate points"""

        lat1 = point1.get('latitude', 0)
        lon1 = point1.get('longitude', 0)
        lat2 = point2.get('latitude', 0)
        lon2 = point2.get('longitude', 0)

        # Simple Euclidean distance for optimization
        # In production, would use proper geographic distance
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Approximate km per degree


class DeliveryAnalyticsService:
    """Service for delivery analytics and insights"""

    def get_transporter_performance(self, transporter_id: int,
                                   start_date: datetime = None,
                                   end_date: datetime = None) -> Dict[str, Any]:
        """Get performance metrics for a transporter"""

        transporter = User.objects.get(id=transporter_id, role='TRANSPORTER')

        # Filter deliveries by date range if provided
        deliveries = Delivery.objects.filter(transporter=transporter)

        if start_date:
            deliveries = deliveries.filter(created_at__gte=start_date)
        if end_date:
            deliveries = deliveries.filter(created_at__lte=end_date)

        total_deliveries = deliveries.count()
        successful_deliveries = deliveries.filter(status='delivered').count()
        failed_deliveries = deliveries.filter(status__in=['failed', 'cancelled']).count()

        # Calculate averages
        avg_rating = deliveries.aggregate(
            avg_rating=Avg('customer_rating')
        )['avg_rating'] or 0

        # On-time delivery rate
        on_time_deliveries = deliveries.filter(
            status='delivered',
            actual_delivery_time__lte=F('scheduled_delivery_time')
        ).count()

        on_time_rate = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0

        # Revenue calculations
        total_revenue = deliveries.aggregate(
            total=Sum('delivery_cost')
        )['total'] or Decimal('0')

        return {
            'transporter_id': transporter_id,
            'transporter_name': transporter.get_full_name(),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics': {
                'total_deliveries': total_deliveries,
                'successful_deliveries': successful_deliveries,
                'failed_deliveries': failed_deliveries,
                'success_rate': (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
                'on_time_deliveries': on_time_deliveries,
                'on_time_rate': on_time_rate,
                'average_rating': float(avg_rating),
                'total_revenue': float(total_revenue)
            }
        }

    def get_delivery_zone_analytics(self, zone_id: int) -> Dict[str, Any]:
        """Get analytics for a specific delivery zone"""

        zone = DeliveryZone.objects.get(id=zone_id)

        # Get deliveries in this zone (simplified - would use geographic queries in production)
        deliveries = Delivery.objects.filter(
            delivery_location__icontains=zone.name  # Simplified matching
        )

        total_deliveries = deliveries.count()
        successful_deliveries = deliveries.filter(status='delivered').count()

        # Average delivery time
        completed_deliveries = deliveries.filter(
            status='delivered',
            actual_delivery_time__isnull=False
        )

        avg_delivery_time = None
        if completed_deliveries.exists():
            # Calculate average time from pickup to delivery
            time_diffs = []
            for delivery in completed_deliveries:
                if delivery.actual_pickup_time and delivery.actual_delivery_time:
                    diff = delivery.actual_delivery_time - delivery.actual_pickup_time
                    time_diffs.append(diff.total_seconds() / 60)  # Convert to minutes

            if time_diffs:
                avg_delivery_time = sum(time_diffs) / len(time_diffs)

        return {
            'zone_id': zone_id,
            'zone_name': zone.name,
            'zone_area_km2': float(zone.coverage_area_km2) if zone.coverage_area_km2 else None,
            'metrics': {
                'total_deliveries': total_deliveries,
                'successful_deliveries': successful_deliveries,
                'success_rate': (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
                'average_delivery_time_minutes': avg_delivery_time,
                'base_delivery_cost': float(zone.base_delivery_cost),
                'cost_per_km': float(zone.cost_per_km)
            },
            'service_availability': {
                'service_days': zone.service_days,
                'service_hours': zone.service_hours,
                'is_active': zone.is_active
            }
        }