from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import timedelta, date
from decimal import Decimal

from core.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import (
    PriceHistory, PricePrediction, DemandForecast, ProductRecommendation,
    MarketInsight, UserInteraction, AIModelMetrics
)
from .serializers import (
    PriceHistorySerializer, PricePredictionSerializer, BulkPricePredictionSerializer,
    DemandForecastSerializer, DemandForecastRequestSerializer,
    ProductRecommendationSerializer, RecommendationRequestSerializer,
    RecommendationInteractionSerializer, MarketInsightSerializer,
    UserInteractionSerializer, InteractionTrackingSerializer,
    AIModelMetricsSerializer, AIAnalyticsSerializer, GenerateInsightsSerializer
)
from .services import (
    PricePredictionService, DemandForecastingService, RecommendationService,
    MarketInsightsService, track_user_interaction
)
from products.models import Product, ProductCategory

User = get_user_model()


class PriceHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing price history data"""
    serializer_class = PriceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['product', 'county', 'source', 'market_location']
    search_fields = ['product__name', 'market_location', 'county']
    ordering_fields = ['date', 'price', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        return PriceHistory.objects.select_related('product', 'product__category')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only farmers and admins can modify price history
            return [permissions.IsAuthenticated(), IsAdminOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def latest_prices(self, request):
        """Get latest prices for all products"""
        latest_prices = PriceHistory.objects.select_related('product').order_by(
            'product', '-date'
        ).distinct('product')

        page = self.paginate_queryset(latest_prices)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(latest_prices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def price_trends(self, request):
        """Get price trends for a specific product"""
        product_id = request.query_params.get('product_id')
        days = int(request.query_params.get('days', 30))

        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = timezone.now().date() - timedelta(days=days)
        price_history = PriceHistory.objects.filter(
            product_id=product_id,
            date__gte=start_date
        ).order_by('date')

        serializer = self.get_serializer(price_history, many=True)
        return Response({
            'product_id': product_id,
            'period_days': days,
            'price_history': serializer.data
        })


class PricePredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing price predictions"""
    serializer_class = PricePredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'prediction_horizon', 'target_date']
    ordering_fields = ['prediction_date', 'target_date', 'confidence_score', 'price_change_percentage']
    ordering = ['-prediction_date']

    def get_queryset(self):
        return PricePrediction.objects.select_related('product', 'product__category')

    @action(detail=False, methods=['post'])
    def generate_prediction(self, request):
        """Generate price prediction for a product"""
        product_id = request.data.get('product_id')
        horizon = request.data.get('prediction_horizon', '1_week')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id, is_active=True)
            prediction = PricePredictionService.predict_price(product, horizon)

            if prediction:
                serializer = self.get_serializer(prediction)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Unable to generate prediction. Insufficient data.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def bulk_generate(self, request):
        """Generate predictions for multiple products"""
        serializer = BulkPricePredictionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data['product_ids']
        horizon = serializer.validated_data['prediction_horizon']

        products = Product.objects.filter(id__in=product_ids, is_active=True)
        predictions = PricePredictionService.bulk_predict_prices(products, horizon)

        prediction_serializer = self.get_serializer(predictions, many=True)
        return Response({
            'predictions_generated': len(predictions),
            'predictions': prediction_serializer.data
        })

    @action(detail=False, methods=['get'])
    def market_overview(self, request):
        """Get market overview with price predictions"""
        # Get recent predictions grouped by category
        recent_predictions = PricePrediction.objects.filter(
            prediction_date__gte=timezone.now().date() - timedelta(days=7)
        ).select_related('product__category')

        overview = {}
        for prediction in recent_predictions:
            category_name = prediction.product.category.name
            if category_name not in overview:
                overview[category_name] = {
                    'category': category_name,
                    'predictions': [],
                    'avg_price_change': 0,
                    'total_products': 0
                }

            overview[category_name]['predictions'].append({
                'product_name': prediction.product.name,
                'current_price': float(prediction.current_price),
                'predicted_price': float(prediction.predicted_price),
                'price_change_percentage': float(prediction.price_change_percentage),
                'confidence_score': float(prediction.confidence_score),
                'target_date': prediction.target_date
            })

        # Calculate averages
        for category_data in overview.values():
            predictions = category_data['predictions']
            if predictions:
                category_data['avg_price_change'] = sum(
                    p['price_change_percentage'] for p in predictions
                ) / len(predictions)
                category_data['total_products'] = len(predictions)

        return Response(list(overview.values()))


class DemandForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing demand forecasts"""
    serializer_class = DemandForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['forecast_type', 'product', 'category', 'region']
    ordering_fields = ['forecast_date', 'confidence_score', 'demand_change_percentage']
    ordering = ['-forecast_date']

    def get_queryset(self):
        return DemandForecast.objects.select_related('product', 'category')

    @action(detail=False, methods=['post'])
    def generate_forecast(self, request):
        """Generate demand forecast"""
        serializer = DemandForecastRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        forecast_type = serializer.validated_data['forecast_type']
        product_id = serializer.validated_data.get('product_id')
        category_id = serializer.validated_data.get('category_id')
        region = serializer.validated_data.get('region')
        forecast_days = serializer.validated_data['forecast_days']

        product = None
        category = None

        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id, is_active=True)
            except ProductCategory.DoesNotExist:
                return Response(
                    {'error': 'Category not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        forecast = DemandForecastingService.forecast_demand(
            product=product,
            category=category,
            region=region,
            forecast_days=forecast_days
        )

        if forecast:
            forecast_serializer = self.get_serializer(forecast)
            return Response(forecast_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Unable to generate forecast. Insufficient data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def regional_overview(self, request):
        """Get regional demand overview"""
        region = request.query_params.get('region')

        if not region:
            return Response(
                {'error': 'region parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        forecasts = DemandForecast.objects.filter(
            region__icontains=region,
            forecast_date__gte=timezone.now().date() - timedelta(days=7)
        ).select_related('product', 'category')

        serializer = self.get_serializer(forecasts, many=True)
        return Response({
            'region': region,
            'forecasts': serializer.data,
            'total_forecasts': len(forecasts)
        })


class ProductRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing product recommendations"""
    serializer_class = ProductRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['recommendation_type', 'is_viewed', 'is_clicked', 'is_purchased']
    ordering_fields = ['score', 'created_at']
    ordering = ['-score', '-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProductRecommendation.objects.select_related('user', 'product', 'product__category')
        return ProductRecommendation.objects.filter(user=self.request.user).select_related(
            'product', 'product__category'
        )

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate recommendations for user"""
        serializer = RecommendationRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        recommendation_type = serializer.validated_data['recommendation_type']
        limit = serializer.validated_data['limit']
        user_id = serializer.validated_data.get('user_id')

        # Determine target user
        target_user = request.user
        if user_id and request.user.is_staff:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        recommendations = RecommendationService.generate_recommendations(
            user=target_user,
            recommendation_type=recommendation_type,
            limit=limit
        )

        recommendation_serializer = self.get_serializer(recommendations, many=True)
        return Response({
            'recommendations_generated': len(recommendations),
            'recommendations': recommendation_serializer.data
        })

    @action(detail=False, methods=['post'])
    def track_interaction(self, request):
        """Track recommendation interaction"""
        serializer = RecommendationInteractionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        interaction_type = serializer.validated_data['interaction_type']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
            RecommendationService.track_recommendation_interaction(
                user=request.user,
                product=product,
                interaction_type=interaction_type
            )

            return Response({'message': 'Interaction tracked successfully'})

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_recommendations(self, request):
        """Get current user's recommendations"""
        recommendations = ProductRecommendation.objects.filter(
            user=request.user
        ).select_related('product', 'product__category')[:20]

        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def performance_stats(self, request):
        """Get recommendation performance statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can view performance stats'},
                status=status.HTTP_403_FORBIDDEN
            )

        total_recommendations = ProductRecommendation.objects.count()
        viewed_recommendations = ProductRecommendation.objects.filter(is_viewed=True).count()
        clicked_recommendations = ProductRecommendation.objects.filter(is_clicked=True).count()
        purchased_recommendations = ProductRecommendation.objects.filter(is_purchased=True).count()

        view_rate = (viewed_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
        click_rate = (clicked_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
        conversion_rate = (purchased_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0

        return Response({
            'total_recommendations': total_recommendations,
            'viewed_recommendations': viewed_recommendations,
            'clicked_recommendations': clicked_recommendations,
            'purchased_recommendations': purchased_recommendations,
            'view_rate': round(view_rate, 2),
            'click_rate': round(click_rate, 2),
            'conversion_rate': round(conversion_rate, 2)
        })


class MarketInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing market insights"""
    serializer_class = MarketInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['insight_type', 'priority', 'product', 'category', 'region', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'created_at', 'valid_until']
    ordering = ['-priority', '-created_at']

    def get_queryset(self):
        queryset = MarketInsight.objects.filter(
            Q(valid_until__gte=timezone.now().date()) | Q(valid_until__isnull=True),
            is_active=True
        ).select_related('product', 'category')

        # Filter by user role
        user_role = getattr(self.request.user, 'role', 'farmer')
        queryset = queryset.filter(target_roles__contains=[user_role])

        return queryset

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generate_insights(self, request):
        """Generate new market insights"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can generate insights'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = GenerateInsightsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        insight_types = serializer.validated_data['insight_types']
        insights_generated = []

        for insight_type in insight_types:
            if insight_type == 'price_trend':
                insights = MarketInsightsService.generate_price_trend_insights()
                insights_generated.extend(insights)
            elif insight_type == 'supply_demand':
                insights = MarketInsightsService.generate_demand_supply_insights()
                insights_generated.extend(insights)
            elif insight_type == 'seasonal_pattern':
                insights = MarketInsightsService.generate_seasonal_insights()
                insights_generated.extend(insights)
            elif insight_type == 'opportunity_alert':
                insights = MarketInsightsService.generate_opportunity_alerts()
                insights_generated.extend(insights)

        insight_serializer = self.get_serializer(insights_generated, many=True)
        return Response({
            'insights_generated': len(insights_generated),
            'insights': insight_serializer.data
        })

    @action(detail=False, methods=['get'])
    def urgent_insights(self, request):
        """Get urgent insights for the user"""
        urgent_insights = self.get_queryset().filter(priority='urgent')
        serializer = self.get_serializer(urgent_insights, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def regional_insights(self, request):
        """Get insights for a specific region"""
        region = request.query_params.get('region')

        if not region:
            return Response(
                {'error': 'region parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        regional_insights = self.get_queryset().filter(
            Q(region__icontains=region) | Q(region__isnull=True)
        )

        serializer = self.get_serializer(regional_insights, many=True)
        return Response({
            'region': region,
            'insights': serializer.data
        })


class UserInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user interactions"""
    serializer_class = UserInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['interaction_type', 'product', 'device_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserInteraction.objects.select_related('user', 'product')
        return UserInteraction.objects.filter(user=self.request.user).select_related('product')

    @action(detail=False, methods=['post'])
    def track(self, request):
        """Track user interaction"""
        serializer = InteractionTrackingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract request metadata
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR')
        referrer = request.META.get('HTTP_REFERER', '')

        # Get product if specified
        product = None
        product_id = serializer.validated_data.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Track interaction
        track_user_interaction(
            user=request.user,
            product=product,
            interaction_type=serializer.validated_data['interaction_type'],
            search_query=serializer.validated_data.get('search_query'),
            session_id=serializer.validated_data.get('session_id'),
            duration=serializer.validated_data.get('duration'),
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            device_type=serializer.validated_data.get('device_type'),
            metadata=serializer.validated_data.get('metadata', {})
        )

        return Response({'message': 'Interaction tracked successfully'})

    @action(detail=False, methods=['get'])
    def my_analytics(self, request):
        """Get current user's interaction analytics"""
        user_interactions = UserInteraction.objects.filter(user=request.user)

        analytics = {
            'total_interactions': user_interactions.count(),
            'interaction_breakdown': {},
            'top_products': [],
            'recent_searches': []
        }

        # Interaction breakdown
        for interaction_type, _ in UserInteraction.INTERACTION_TYPE_CHOICES:
            count = user_interactions.filter(interaction_type=interaction_type).count()
            analytics['interaction_breakdown'][interaction_type] = count

        # Top products
        product_interactions = user_interactions.filter(
            product__isnull=False
        ).values('product__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        analytics['top_products'] = list(product_interactions)

        # Recent searches
        recent_searches = user_interactions.filter(
            interaction_type='search',
            search_query__isnull=False
        ).values_list('search_query', flat=True)[:20]

        analytics['recent_searches'] = list(recent_searches)

        return Response(analytics)


class AIModelMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing AI model metrics"""
    serializer_class = AIModelMetricsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['model_type', 'is_active']
    ordering_fields = ['training_date', 'accuracy', 'predictions_made']
    ordering = ['-training_date']

    def get_queryset(self):
        return AIModelMetrics.objects.all()

    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Get AI model performance summary"""
        models = AIModelMetrics.objects.filter(is_active=True)

        summary = {
            'total_models': models.count(),
            'models_by_type': {},
            'average_accuracy': 0,
            'total_predictions': 0
        }

        for model_type, _ in AIModelMetrics.MODEL_TYPE_CHOICES:
            type_models = models.filter(model_type=model_type)
            summary['models_by_type'][model_type] = {
                'count': type_models.count(),
                'avg_accuracy': type_models.aggregate(avg=Avg('accuracy'))['avg'] or 0,
                'total_predictions': type_models.aggregate(total=Sum('predictions_made'))['total'] or 0
            }

        # Overall averages
        summary['average_accuracy'] = models.aggregate(avg=Avg('accuracy'))['avg'] or 0
        summary['total_predictions'] = models.aggregate(total=Sum('predictions_made'))['total'] or 0

        return Response(summary)


class AIAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for AI analytics dashboard"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get AI analytics dashboard data"""
        # Calculate various metrics
        total_predictions = PricePrediction.objects.count()
        total_recommendations = ProductRecommendation.objects.count()
        total_insights = MarketInsight.objects.count()
        total_interactions = UserInteraction.objects.count()

        # Performance metrics
        avg_prediction_accuracy = PricePrediction.objects.aggregate(
            avg=Avg('confidence_score')
        )['avg'] or 0

        recommendation_stats = ProductRecommendation.objects.aggregate(
            total=Count('id'),
            clicked=Count('id', filter=Q(is_clicked=True)),
            purchased=Count('id', filter=Q(is_purchased=True))
        )

        click_rate = (recommendation_stats['clicked'] / recommendation_stats['total'] * 100) if recommendation_stats['total'] > 0 else 0
        conversion_rate = (recommendation_stats['purchased'] / recommendation_stats['total'] * 100) if recommendation_stats['total'] > 0 else 0

        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        predictions_last_7_days = PricePrediction.objects.filter(created_at__gte=seven_days_ago).count()
        recommendations_last_7_days = ProductRecommendation.objects.filter(created_at__gte=seven_days_ago).count()
        insights_last_7_days = MarketInsight.objects.filter(created_at__gte=seven_days_ago).count()

        # Top performing models
        top_models = list(AIModelMetrics.objects.filter(is_active=True).order_by('-accuracy')[:5].values(
            'model_type', 'model_version', 'accuracy', 'predictions_made'
        ))

        # Interaction breakdown
        interaction_breakdown = {}
        for interaction_type, _ in UserInteraction.INTERACTION_TYPE_CHOICES:
            count = UserInteraction.objects.filter(interaction_type=interaction_type).count()
            interaction_breakdown[interaction_type] = count

        # Recommendation type breakdown
        recommendation_type_breakdown = {}
        for rec_type, _ in ProductRecommendation.RECOMMENDATION_TYPE_CHOICES:
            count = ProductRecommendation.objects.filter(recommendation_type=rec_type).count()
            recommendation_type_breakdown[rec_type] = count

        analytics_data = {
            'total_predictions': total_predictions,
            'total_recommendations': total_recommendations,
            'total_insights': total_insights,
            'total_interactions': total_interactions,
            'avg_prediction_accuracy': float(avg_prediction_accuracy),
            'recommendation_click_rate': round(click_rate, 2),
            'recommendation_conversion_rate': round(conversion_rate, 2),
            'predictions_last_7_days': predictions_last_7_days,
            'recommendations_last_7_days': recommendations_last_7_days,
            'insights_last_7_days': insights_last_7_days,
            'top_models': top_models,
            'interaction_breakdown': interaction_breakdown,
            'recommendation_type_breakdown': recommendation_type_breakdown
        }

        serializer = AIAnalyticsSerializer(data=analytics_data)
        serializer.is_valid()
        return Response(serializer.data)