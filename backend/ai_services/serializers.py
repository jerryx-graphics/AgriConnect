from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import (
    PriceHistory, PricePrediction, DemandForecast, ProductRecommendation,
    MarketInsight, UserInteraction, AIModelMetrics
)
from products.serializers import ProductDetailSerializer, ProductCategorySerializer

User = get_user_model()


class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'product_name', 'category_name', 'price', 'date',
            'market_location', 'county', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value


class PricePredictionSerializer(serializers.ModelSerializer):
    product_details = ProductDetailSerializer(source='product', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    price_trend = serializers.SerializerMethodField()

    class Meta:
        model = PricePrediction
        fields = [
            'id', 'product', 'product_details', 'product_name', 'category_name',
            'predicted_price', 'current_price', 'price_change_percentage', 'price_trend',
            'prediction_horizon', 'confidence_score', 'prediction_date', 'target_date',
            'model_version', 'features_used', 'market_conditions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_price_trend(self, obj):
        if obj.price_change_percentage > 0:
            return 'increasing'
        elif obj.price_change_percentage < 0:
            return 'decreasing'
        return 'stable'


class BulkPricePredictionSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )
    prediction_horizon = serializers.ChoiceField(
        choices=PricePrediction.PREDICTION_HORIZON_CHOICES,
        default='1_week'
    )

    def validate_product_ids(self, value):
        from products.models import Product

        existing_ids = Product.objects.filter(id__in=value, is_active=True).count()
        if existing_ids != len(value):
            raise serializers.ValidationError("Some product IDs are invalid or inactive")
        return value


class DemandForecastSerializer(serializers.ModelSerializer):
    product_details = ProductDetailSerializer(source='product', read_only=True)
    category_details = ProductCategorySerializer(source='category', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    forecast_period_days = serializers.SerializerMethodField()
    demand_trend = serializers.SerializerMethodField()

    class Meta:
        model = DemandForecast
        fields = [
            'id', 'forecast_type', 'product', 'product_details', 'product_name',
            'category', 'category_details', 'category_name', 'region',
            'forecast_date', 'forecast_period_start', 'forecast_period_end', 'forecast_period_days',
            'predicted_demand_quantity', 'predicted_demand_value', 'historical_average',
            'demand_change_percentage', 'demand_trend', 'seasonal_factor', 'weather_impact',
            'market_trend_factor', 'confidence_score', 'peak_demand_day',
            'demand_pattern', 'factors', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_forecast_period_days(self, obj):
        return (obj.forecast_period_end - obj.forecast_period_start).days + 1

    def get_demand_trend(self, obj):
        if obj.demand_change_percentage > 5:
            return 'increasing'
        elif obj.demand_change_percentage < -5:
            return 'decreasing'
        return 'stable'


class DemandForecastRequestSerializer(serializers.Serializer):
    forecast_type = serializers.ChoiceField(choices=DemandForecast.FORECAST_TYPE_CHOICES)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    forecast_days = serializers.IntegerField(min_value=1, max_value=365, default=30)

    def validate(self, data):
        forecast_type = data.get('forecast_type')

        if forecast_type == 'product' and not data.get('product_id'):
            raise serializers.ValidationError("product_id is required for product-level forecasts")
        elif forecast_type == 'category' and not data.get('category_id'):
            raise serializers.ValidationError("category_id is required for category-level forecasts")
        elif forecast_type == 'regional' and not data.get('region'):
            raise serializers.ValidationError("region is required for regional forecasts")

        return data


class ProductRecommendationSerializer(serializers.ModelSerializer):
    product_details = ProductDetailSerializer(source='product', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price_per_unit', max_digits=10, decimal_places=2, read_only=True)
    farmer_name = serializers.CharField(source='product.farmer.get_full_name', read_only=True)

    class Meta:
        model = ProductRecommendation
        fields = [
            'id', 'user', 'user_email', 'product', 'product_details', 'product_name',
            'category_name', 'product_price', 'farmer_name', 'recommendation_type',
            'score', 'reason', 'user_interaction_history', 'similar_users',
            'product_features', 'is_viewed', 'is_clicked', 'is_purchased',
            'viewed_at', 'clicked_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationRequestSerializer(serializers.Serializer):
    recommendation_type = serializers.ChoiceField(
        choices=ProductRecommendation.RECOMMENDATION_TYPE_CHOICES,
        default='hybrid'
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    user_id = serializers.UUIDField(required=False, help_text="For admin use - recommend for specific user")

    def validate_user_id(self, value):
        if value:
            request = self.context.get('request')
            if not request or not request.user.is_staff:
                raise serializers.ValidationError("Only admin users can generate recommendations for other users")
        return value


class RecommendationInteractionSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    interaction_type = serializers.ChoiceField(choices=['view', 'click', 'purchase'])

    def validate_product_id(self, value):
        from products.models import Product

        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product not found or inactive")
        return value


class MarketInsightSerializer(serializers.ModelSerializer):
    product_details = ProductDetailSerializer(source='product', read_only=True)
    category_details = ProductCategorySerializer(source='category', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_relevant_for_user = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = MarketInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'product', 'product_details',
            'product_name', 'category', 'category_details', 'category_name', 'region',
            'key_metrics', 'trends', 'recommendations', 'target_roles', 'priority',
            'valid_from', 'valid_until', 'days_until_expiry', 'is_active',
            'is_relevant_for_user', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_is_relevant_for_user(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return True

        user_role = getattr(request.user, 'role', 'farmer')
        return user_role in obj.target_roles

    def get_days_until_expiry(self, obj):
        if not obj.valid_until:
            return None

        from django.utils import timezone
        today = timezone.now().date()
        return (obj.valid_until - today).days


class UserInteractionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = UserInteraction
        fields = [
            'id', 'user', 'user_email', 'product', 'product_name', 'interaction_type',
            'search_query', 'session_id', 'duration', 'referrer', 'user_agent',
            'ip_address', 'device_type', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InteractionTrackingSerializer(serializers.Serializer):
    interaction_type = serializers.ChoiceField(choices=UserInteraction.INTERACTION_TYPE_CHOICES)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    search_query = serializers.CharField(max_length=200, required=False, allow_blank=True)
    session_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    duration = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    referrer = serializers.CharField(max_length=200, required=False, allow_blank=True)
    device_type = serializers.CharField(max_length=20, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)

    def validate(self, data):
        interaction_type = data.get('interaction_type')

        # Some interactions require a product
        if interaction_type in ['view', 'add_to_cart', 'purchase', 'review', 'wishlist', 'share', 'compare']:
            if not data.get('product_id'):
                raise serializers.ValidationError(f"{interaction_type} interaction requires a product_id")

        # Search interactions require a search query
        if interaction_type == 'search' and not data.get('search_query'):
            raise serializers.ValidationError("Search interaction requires a search_query")

        return data

    def validate_product_id(self, value):
        if value:
            from products.models import Product
            if not Product.objects.filter(id=value, is_active=True).exists():
                raise serializers.ValidationError("Product not found or inactive")
        return value


class AIModelMetricsSerializer(serializers.ModelSerializer):
    performance_score = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = AIModelMetrics
        fields = [
            'id', 'model_type', 'model_version', 'accuracy', 'precision', 'recall',
            'f1_score', 'mae', 'mse', 'performance_score', 'training_date',
            'training_data_size', 'features_count', 'parameters', 'predictions_made',
            'avg_response_time', 'is_active', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_performance_score(self, obj):
        # Calculate overall performance score
        scores = []

        if obj.accuracy is not None:
            scores.append(float(obj.accuracy))
        if obj.f1_score is not None:
            scores.append(float(obj.f1_score))

        if scores:
            return sum(scores) / len(scores)
        return None

    def get_status(self, obj):
        if not obj.is_active:
            return 'inactive'
        elif obj.predictions_made == 0:
            return 'not_deployed'
        elif obj.predictions_made < 100:
            return 'testing'
        else:
            return 'production'


class AIAnalyticsSerializer(serializers.Serializer):
    """Serializer for AI analytics dashboard data"""
    total_predictions = serializers.IntegerField(read_only=True)
    total_recommendations = serializers.IntegerField(read_only=True)
    total_insights = serializers.IntegerField(read_only=True)
    total_interactions = serializers.IntegerField(read_only=True)

    # Performance metrics
    avg_prediction_accuracy = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    recommendation_click_rate = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    recommendation_conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)

    # Recent activity
    predictions_last_7_days = serializers.IntegerField(read_only=True)
    recommendations_last_7_days = serializers.IntegerField(read_only=True)
    insights_last_7_days = serializers.IntegerField(read_only=True)

    # Top performing models
    top_models = serializers.ListField(child=serializers.DictField(), read_only=True)

    # Usage by type
    interaction_breakdown = serializers.DictField(read_only=True)
    recommendation_type_breakdown = serializers.DictField(read_only=True)


class GenerateInsightsSerializer(serializers.Serializer):
    insight_types = serializers.MultipleChoiceField(
        choices=MarketInsight.INSIGHT_TYPE_CHOICES,
        default=['price_trend', 'supply_demand', 'seasonal_pattern', 'opportunity_alert']
    )
    target_roles = serializers.ListField(
        child=serializers.CharField(max_length=20),
        default=['farmer', 'buyer', 'cooperative'],
        required=False
    )
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    product_categories = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Generate insights for specific product categories"
    )

    def validate_product_categories(self, value):
        if value:
            from products.models import ProductCategory
            existing_ids = ProductCategory.objects.filter(id__in=value, is_active=True).count()
            if existing_ids != len(value):
                raise serializers.ValidationError("Some category IDs are invalid or inactive")
        return value