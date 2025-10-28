from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    PriceHistory, PricePrediction, DemandForecast, ProductRecommendation,
    MarketInsight, UserInteraction, AIModelMetrics
)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'date', 'market_location', 'county', 'source']
    list_filter = ['source', 'county', 'date', 'product__category']
    search_fields = ['product__name', 'market_location', 'county']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'product__category')


@admin.register(PricePrediction)
class PricePredictionAdmin(admin.ModelAdmin):
    list_display = ['product', 'predicted_price', 'current_price', 'price_change_display',
                    'prediction_horizon', 'confidence_score', 'target_date']
    list_filter = ['prediction_horizon', 'prediction_date', 'product__category']
    search_fields = ['product__name']
    date_hierarchy = 'prediction_date'
    readonly_fields = ['created_at', 'updated_at', 'features_used', 'market_conditions']

    def price_change_display(self, obj):
        change = obj.price_change_percentage
        color = 'green' if change > 0 else 'red' if change < 0 else 'black'
        symbol = '↑' if change > 0 else '↓' if change < 0 else '→'
        return format_html(
            '<span style="color: {};">{} {}%</span>',
            color, symbol, abs(change)
        )
    price_change_display.short_description = 'Price Change'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'product__category')


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['forecast_type', 'get_target', 'predicted_demand_quantity',
                    'demand_change_percentage', 'confidence_score', 'forecast_date']
    list_filter = ['forecast_type', 'forecast_date', 'region']
    search_fields = ['product__name', 'category__name', 'region']
    date_hierarchy = 'forecast_date'
    readonly_fields = ['created_at', 'updated_at', 'demand_pattern', 'factors']

    def get_target(self, obj):
        if obj.product:
            return f"Product: {obj.product.name}"
        elif obj.category:
            return f"Category: {obj.category.name}"
        else:
            return f"Region: {obj.region}"
    get_target.short_description = 'Target'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'category')


@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'recommendation_type', 'score',
                    'interaction_status', 'created_at']
    list_filter = ['recommendation_type', 'is_viewed', 'is_clicked', 'is_purchased', 'created_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'user_interaction_history',
                       'similar_users', 'product_features']

    def interaction_status(self, obj):
        statuses = []
        if obj.is_viewed:
            statuses.append('<span style="color: blue;">Viewed</span>')
        if obj.is_clicked:
            statuses.append('<span style="color: orange;">Clicked</span>')
        if obj.is_purchased:
            statuses.append('<span style="color: green;">Purchased</span>')

        return mark_safe(' | '.join(statuses)) if statuses else 'No interactions'
    interaction_status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product', 'product__category')


@admin.register(MarketInsight)
class MarketInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'insight_type', 'priority', 'get_target_entity',
                    'is_active', 'valid_until']
    list_filter = ['insight_type', 'priority', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'key_metrics', 'trends', 'recommendations']

    def get_target_entity(self, obj):
        if obj.product:
            return f"Product: {obj.product.name}"
        elif obj.category:
            return f"Category: {obj.category.name}"
        elif obj.region:
            return f"Region: {obj.region}"
        return "General"
    get_target_entity.short_description = 'Target'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'category')


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'interaction_type', 'search_query',
                    'device_type', 'created_at']
    list_filter = ['interaction_type', 'device_type', 'created_at']
    search_fields = ['user__email', 'product__name', 'search_query']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'metadata']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')


@admin.register(AIModelMetrics)
class AIModelMetricsAdmin(admin.ModelAdmin):
    list_display = ['model_type', 'model_version', 'accuracy', 'precision',
                    'recall', 'predictions_made', 'is_active', 'training_date']
    list_filter = ['model_type', 'is_active', 'training_date']
    search_fields = ['model_type', 'model_version']
    readonly_fields = ['created_at', 'updated_at', 'parameters']

    fieldsets = (
        (None, {
            'fields': ('model_type', 'model_version', 'is_active')
        }),
        ('Performance Metrics', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score', 'mae', 'mse')
        }),
        ('Training Information', {
            'fields': ('training_date', 'training_data_size', 'features_count', 'parameters')
        }),
        ('Production Metrics', {
            'fields': ('predictions_made', 'avg_response_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )