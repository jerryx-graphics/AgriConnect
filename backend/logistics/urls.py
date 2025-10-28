from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    VehicleViewSet, TransportCompanyViewSet, DeliveryRouteViewSet,
    DeliveryViewSet, DeliveryTrackingViewSet, DeliveryZoneViewSet,
    RouteOptimizationViewSet, DeliveryFeedbackViewSet, LogisticsAPIViewSet
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'companies', TransportCompanyViewSet, basename='transport-companies')
router.register(r'routes', DeliveryRouteViewSet, basename='delivery-routes')
router.register(r'deliveries', DeliveryViewSet, basename='deliveries')
router.register(r'tracking', DeliveryTrackingViewSet, basename='delivery-tracking')
router.register(r'zones', DeliveryZoneViewSet, basename='delivery-zones')
router.register(r'optimization', RouteOptimizationViewSet, basename='route-optimization')
router.register(r'feedback', DeliveryFeedbackViewSet, basename='delivery-feedback')
router.register(r'api', LogisticsAPIViewSet, basename='logistics-api')

urlpatterns = [
    path('', include(router.urls)),
]