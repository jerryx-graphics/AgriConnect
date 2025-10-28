from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PriceHistoryViewSet, PricePredictionViewSet, DemandForecastViewSet,
    ProductRecommendationViewSet, MarketInsightViewSet, UserInteractionViewSet,
    AIModelMetricsViewSet, AIAnalyticsViewSet
)

app_name = 'ai_services'

router = DefaultRouter()
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')
router.register(r'price-predictions', PricePredictionViewSet, basename='price-predictions')
router.register(r'demand-forecasts', DemandForecastViewSet, basename='demand-forecasts')
router.register(r'recommendations', ProductRecommendationViewSet, basename='recommendations')
router.register(r'insights', MarketInsightViewSet, basename='insights')
router.register(r'interactions', UserInteractionViewSet, basename='interactions')
router.register(r'model-metrics', AIModelMetricsViewSet, basename='model-metrics')
router.register(r'analytics', AIAnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]