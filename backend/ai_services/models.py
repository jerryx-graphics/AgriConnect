from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import BaseModel
from products.models import Product, ProductCategory

User = get_user_model()


class PriceHistory(BaseModel):
    """Historical price data for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ai_price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    market_location = models.CharField(max_length=100, help_text="Market or location where price was recorded")
    county = models.CharField(max_length=100)
    source = models.CharField(max_length=50, choices=[
        ('manual', 'Manual Entry'),
        ('api', 'API Feed'),
        ('scraping', 'Web Scraping'),
        ('user_reported', 'User Reported')
    ], default='manual')

    class Meta:
        ordering = ['-date']
        unique_together = ['product', 'date', 'market_location']

    def __str__(self):
        return f"{self.product.name} - KSH {self.price} on {self.date}"


class PricePrediction(BaseModel):
    """AI-generated price predictions for products"""
    PREDICTION_HORIZON_CHOICES = [
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('2_weeks', '2 Weeks'),
        ('1_month', '1 Month'),
        ('3_months', '3 Months')
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_predictions')
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_change_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    prediction_horizon = models.CharField(max_length=10, choices=PREDICTION_HORIZON_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence level as percentage (0-100)"
    )
    prediction_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(help_text="Date for which the prediction is made")

    # AI Model metadata
    model_version = models.CharField(max_length=20, default='1.0')
    features_used = models.JSONField(default=list, help_text="List of features used in prediction")
    market_conditions = models.JSONField(default=dict, help_text="Market conditions at prediction time")

    class Meta:
        ordering = ['-prediction_date']
        unique_together = ['product', 'prediction_horizon', 'target_date']

    def __str__(self):
        return f"{self.product.name} - KSH {self.predicted_price} ({self.prediction_horizon})"


class DemandForecast(BaseModel):
    """Demand forecasting for products and categories"""
    FORECAST_TYPE_CHOICES = [
        ('product', 'Product Level'),
        ('category', 'Category Level'),
        ('regional', 'Regional Level')
    ]

    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='demand_forecasts')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='demand_forecasts')
    region = models.CharField(max_length=100, null=True, blank=True, help_text="County or specific region")

    forecast_date = models.DateField(auto_now_add=True)
    forecast_period_start = models.DateField()
    forecast_period_end = models.DateField()

    # Demand metrics
    predicted_demand_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_demand_value = models.DecimalField(max_digits=15, decimal_places=2)
    historical_average = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    demand_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Factors affecting demand
    seasonal_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    weather_impact = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    market_trend_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Additional insights
    peak_demand_day = models.CharField(max_length=20, null=True, blank=True)
    demand_pattern = models.JSONField(default=dict, help_text="Daily/weekly demand pattern")
    factors = models.JSONField(default=list, help_text="Factors influencing the forecast")

    class Meta:
        ordering = ['-forecast_date']

    def __str__(self):
        if self.product:
            return f"Demand forecast for {self.product.name}"
        elif self.category:
            return f"Demand forecast for {self.category.name} category"
        return f"Regional demand forecast for {self.region}"


class ProductRecommendation(BaseModel):
    """Product recommendations for users"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('hybrid', 'Hybrid'),
        ('trending', 'Trending Products'),
        ('seasonal', 'Seasonal Recommendations'),
        ('location_based', 'Location-Based')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Recommendation score (0-1)"
    )
    reason = models.TextField(help_text="Reason for recommendation")

    # Context data
    user_interaction_history = models.JSONField(default=dict)
    similar_users = models.JSONField(default=list, help_text="IDs of similar users")
    product_features = models.JSONField(default=dict)

    # Tracking
    is_viewed = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ['user', 'product', 'recommendation_type']

    def __str__(self):
        return f"Recommend {self.product.name} to {self.user.email} (score: {self.score})"


class MarketInsight(BaseModel):
    """Market insights and analytics"""
    INSIGHT_TYPE_CHOICES = [
        ('price_trend', 'Price Trend Analysis'),
        ('supply_demand', 'Supply & Demand Analysis'),
        ('seasonal_pattern', 'Seasonal Pattern'),
        ('regional_comparison', 'Regional Price Comparison'),
        ('competition_analysis', 'Competition Analysis'),
        ('opportunity_alert', 'Market Opportunity Alert')
    ]

    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Target entities
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='insights')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='insights')
    region = models.CharField(max_length=100, null=True, blank=True)

    # Insight data
    key_metrics = models.JSONField(default=dict)
    trends = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)

    # Relevance and targeting
    target_roles = models.JSONField(default=list, help_text="User roles this insight is relevant for")
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')

    # Validity period
    valid_from = models.DateField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.insight_type})"


class UserInteraction(BaseModel):
    """Track user interactions for recommendation system"""
    INTERACTION_TYPE_CHOICES = [
        ('view', 'Product View'),
        ('search', 'Search Query'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('review', 'Product Review'),
        ('wishlist', 'Add to Wishlist'),
        ('share', 'Share Product'),
        ('compare', 'Product Comparison')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)

    # Interaction details
    search_query = models.CharField(max_length=200, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in seconds")

    # Context
    referrer = models.CharField(max_length=200, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=20, null=True, blank=True)

    # Additional data
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['product', 'interaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        product_name = self.product.name if self.product else "N/A"
        return f"{self.user.email} - {self.interaction_type} - {product_name}"


class AIModelMetrics(BaseModel):
    """Track AI model performance metrics"""
    MODEL_TYPE_CHOICES = [
        ('price_prediction', 'Price Prediction'),
        ('demand_forecast', 'Demand Forecasting'),
        ('recommendation', 'Product Recommendation'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('image_classification', 'Product Image Classification')
    ]

    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES)
    model_version = models.CharField(max_length=20)

    # Performance metrics
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    mae = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Mean Absolute Error
    mse = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Mean Squared Error

    # Model metadata
    training_date = models.DateTimeField()
    training_data_size = models.PositiveIntegerField()
    features_count = models.PositiveIntegerField()
    parameters = models.JSONField(default=dict)

    # Production metrics
    predictions_made = models.PositiveIntegerField(default=0)
    avg_response_time = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-training_date']
        unique_together = ['model_type', 'model_version']

    def __str__(self):
        return f"{self.model_type} v{self.model_version} - Accuracy: {self.accuracy}"