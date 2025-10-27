import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from django.db.models import Q, Avg, Count, Sum, Max, Min
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json
import logging

from .models import (
    PriceHistory, PricePrediction, DemandForecast, ProductRecommendation,
    MarketInsight, UserInteraction, AIModelMetrics
)
from products.models import Product, ProductCategory
from orders.models import Order, OrderItem

User = get_user_model()
logger = logging.getLogger(__name__)


class PricePredictionService:
    """Service for AI-powered price predictions"""

    @staticmethod
    def predict_price(product: Product, horizon: str = '1_week') -> Optional[PricePrediction]:
        """Generate price prediction for a product"""
        try:
            # Get historical price data
            price_history = PriceHistory.objects.filter(
                product=product
            ).order_by('-date')[:30]  # Last 30 data points

            if len(price_history) < 5:
                logger.warning(f"Insufficient price history for {product.name}")
                return None

            # Simple moving average prediction (can be replaced with ML models)
            prices = [float(p.price) for p in price_history]
            current_price = Decimal(str(prices[0]))

            # Calculate trend
            short_avg = np.mean(prices[:7]) if len(prices) >= 7 else np.mean(prices)
            long_avg = np.mean(prices)
            trend_factor = short_avg / long_avg if long_avg > 0 else 1.0

            # Seasonal adjustment
            seasonal_factor = PricePredictionService._calculate_seasonal_factor(product, horizon)

            # Market conditions adjustment
            market_factor = PricePredictionService._get_market_conditions_factor(product)

            # Calculate predicted price
            predicted_price = current_price * Decimal(str(trend_factor)) * Decimal(str(seasonal_factor)) * Decimal(str(market_factor))

            # Calculate confidence score based on data quality and consistency
            price_variance = np.var(prices) if len(prices) > 1 else 0
            data_quality_score = min(len(price_history) / 30, 1.0) * 100
            volatility_penalty = max(0, 20 - price_variance / np.mean(prices) * 100) if np.mean(prices) > 0 else 0
            confidence_score = min(data_quality_score + volatility_penalty, 100)

            # Calculate price change percentage
            price_change = ((predicted_price - current_price) / current_price * 100) if current_price > 0 else Decimal('0')

            # Target date based on horizon
            target_date = PricePredictionService._calculate_target_date(horizon)

            # Create prediction
            prediction = PricePrediction.objects.create(
                product=product,
                predicted_price=predicted_price,
                current_price=current_price,
                price_change_percentage=price_change,
                prediction_horizon=horizon,
                confidence_score=Decimal(str(confidence_score)),
                target_date=target_date,
                features_used=['moving_average', 'trend', 'seasonal', 'market_conditions'],
                market_conditions={
                    'trend_factor': trend_factor,
                    'seasonal_factor': seasonal_factor,
                    'market_factor': market_factor,
                    'volatility': price_variance
                }
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting price for {product.name}: {str(e)}")
            return None

    @staticmethod
    def _calculate_seasonal_factor(product: Product, horizon: str) -> float:
        """Calculate seasonal adjustment factor"""
        current_month = datetime.now().month

        # Simple seasonal patterns (can be enhanced with historical data)
        seasonal_patterns = {
            'vegetables': {1: 1.2, 2: 1.1, 3: 0.9, 4: 0.8, 5: 0.7, 6: 0.8, 7: 0.9, 8: 1.0, 9: 1.1, 10: 1.2, 11: 1.3, 12: 1.4},
            'fruits': {1: 1.3, 2: 1.2, 3: 1.0, 4: 0.8, 5: 0.6, 6: 0.7, 7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.2, 12: 1.3},
            'grains': {1: 1.1, 2: 1.0, 3: 0.9, 4: 0.9, 5: 1.0, 6: 1.1, 7: 1.2, 8: 1.3, 9: 1.2, 10: 1.1, 11: 1.0, 12: 1.0}
        }

        category_name = product.category.name.lower()
        pattern_key = 'vegetables'  # default

        if 'fruit' in category_name:
            pattern_key = 'fruits'
        elif any(grain in category_name for grain in ['grain', 'cereal', 'maize', 'wheat']):
            pattern_key = 'grains'

        return seasonal_patterns[pattern_key].get(current_month, 1.0)

    @staticmethod
    def _get_market_conditions_factor(product: Product) -> float:
        """Calculate market conditions factor"""
        # Simple market conditions (can be enhanced with external data)
        recent_orders = Order.objects.filter(
            items__product=product,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()

        # High demand increases price
        demand_factor = min(1.0 + (recent_orders / 100), 1.5)

        return demand_factor

    @staticmethod
    def _calculate_target_date(horizon: str) -> date:
        """Calculate target date based on prediction horizon"""
        today = date.today()
        horizon_map = {
            '1_day': timedelta(days=1),
            '3_days': timedelta(days=3),
            '1_week': timedelta(days=7),
            '2_weeks': timedelta(days=14),
            '1_month': timedelta(days=30),
            '3_months': timedelta(days=90)
        }
        return today + horizon_map.get(horizon, timedelta(days=7))

    @staticmethod
    def bulk_predict_prices(products: List[Product], horizon: str = '1_week') -> List[PricePrediction]:
        """Generate predictions for multiple products"""
        predictions = []
        for product in products:
            prediction = PricePredictionService.predict_price(product, horizon)
            if prediction:
                predictions.append(prediction)
        return predictions


class DemandForecastingService:
    """Service for demand forecasting"""

    @staticmethod
    def forecast_demand(
        product: Optional[Product] = None,
        category: Optional[ProductCategory] = None,
        region: Optional[str] = None,
        forecast_days: int = 30
    ) -> Optional[DemandForecast]:
        """Generate demand forecast"""
        try:
            forecast_type = 'product' if product else ('category' if category else 'regional')

            # Get historical demand data
            historical_data = DemandForecastingService._get_historical_demand(
                product, category, region, days=90
            )

            if not historical_data:
                logger.warning("Insufficient historical demand data")
                return None

            # Calculate forecast
            avg_daily_demand = np.mean([d['quantity'] for d in historical_data])
            avg_daily_value = np.mean([d['value'] for d in historical_data])

            # Apply growth trend
            trend_factor = DemandForecastingService._calculate_trend_factor(historical_data)

            # Apply seasonal adjustment
            seasonal_factor = DemandForecastingService._calculate_seasonal_demand_factor(
                product or category, forecast_days
            )

            # Weather impact (simplified)
            weather_factor = 1.0  # Can be enhanced with weather API

            # Market trend factor
            market_trend = DemandForecastingService._calculate_market_trend_factor(
                product, category, region
            )

            # Calculate predictions
            predicted_quantity = avg_daily_demand * forecast_days * trend_factor * seasonal_factor * weather_factor
            predicted_value = avg_daily_value * forecast_days * trend_factor * seasonal_factor * weather_factor

            # Historical average for comparison
            historical_avg = avg_daily_demand * forecast_days
            demand_change = ((predicted_quantity - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0

            # Confidence calculation
            data_points = len(historical_data)
            variance = np.var([d['quantity'] for d in historical_data]) if len(historical_data) > 1 else 0
            confidence = min(80 + (data_points / 90 * 20), 95) - (variance / avg_daily_demand * 10 if avg_daily_demand > 0 else 0)

            # Create forecast
            forecast_start = date.today() + timedelta(days=1)
            forecast_end = forecast_start + timedelta(days=forecast_days - 1)

            forecast = DemandForecast.objects.create(
                forecast_type=forecast_type,
                product=product,
                category=category,
                region=region,
                forecast_period_start=forecast_start,
                forecast_period_end=forecast_end,
                predicted_demand_quantity=Decimal(str(predicted_quantity)),
                predicted_demand_value=Decimal(str(predicted_value)),
                historical_average=Decimal(str(historical_avg)),
                demand_change_percentage=Decimal(str(demand_change)),
                seasonal_factor=Decimal(str(seasonal_factor)),
                weather_impact=Decimal(str(weather_factor)),
                market_trend_factor=Decimal(str(market_trend)),
                confidence_score=Decimal(str(max(confidence, 0))),
                demand_pattern=DemandForecastingService._generate_demand_pattern(historical_data),
                factors=['historical_trend', 'seasonal_pattern', 'market_conditions']
            )

            return forecast

        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            return None

    @staticmethod
    def _get_historical_demand(
        product: Optional[Product],
        category: Optional[ProductCategory],
        region: Optional[str],
        days: int = 90
    ) -> List[Dict]:
        """Get historical demand data"""
        start_date = timezone.now() - timedelta(days=days)

        order_items = OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=['confirmed', 'processing', 'delivered', 'completed']
        )

        if product:
            order_items = order_items.filter(product=product)
        elif category:
            order_items = order_items.filter(product__category=category)

        if region:
            order_items = order_items.filter(order__delivery_county__icontains=region)

        # Group by date
        daily_demand = {}
        for item in order_items:
            date_key = item.order.created_at.date()
            if date_key not in daily_demand:
                daily_demand[date_key] = {'quantity': 0, 'value': 0}
            daily_demand[date_key]['quantity'] += float(item.quantity)
            daily_demand[date_key]['value'] += float(item.total_price)

        return list(daily_demand.values())

    @staticmethod
    def _calculate_trend_factor(historical_data: List[Dict]) -> float:
        """Calculate demand trend factor"""
        if len(historical_data) < 2:
            return 1.0

        quantities = [d['quantity'] for d in historical_data]

        # Simple linear trend
        x = np.arange(len(quantities))
        z = np.polyfit(x, quantities, 1)
        slope = z[0]

        # Convert slope to multiplier
        trend_factor = 1.0 + (slope / np.mean(quantities) if np.mean(quantities) > 0 else 0)
        return max(0.5, min(2.0, trend_factor))  # Clamp between 0.5 and 2.0

    @staticmethod
    def _calculate_seasonal_demand_factor(entity, forecast_days: int) -> float:
        """Calculate seasonal demand factor"""
        current_month = datetime.now().month

        # Simplified seasonal patterns
        seasonal_patterns = {
            'vegetables': {1: 0.8, 2: 0.9, 3: 1.1, 4: 1.3, 5: 1.2, 6: 1.0, 7: 0.9, 8: 0.8, 9: 1.0, 10: 1.2, 11: 1.1, 12: 0.9},
            'fruits': {1: 0.7, 2: 0.8, 3: 1.0, 4: 1.4, 5: 1.5, 6: 1.3, 7: 1.1, 8: 1.0, 9: 0.9, 10: 0.8, 11: 0.7, 12: 0.8},
            'grains': {1: 1.0, 2: 1.0, 3: 1.1, 4: 1.1, 5: 1.0, 6: 0.9, 7: 0.8, 8: 0.7, 9: 0.8, 10: 0.9, 11: 1.0, 12: 1.0}
        }

        # Default pattern
        pattern = seasonal_patterns['vegetables']
        return pattern.get(current_month, 1.0)

    @staticmethod
    def _calculate_market_trend_factor(
        product: Optional[Product],
        category: Optional[ProductCategory],
        region: Optional[str]
    ) -> float:
        """Calculate market trend factor"""
        # Simple market trend based on recent activity
        recent_orders = Order.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )

        if product:
            recent_orders = recent_orders.filter(items__product=product)
        elif category:
            recent_orders = recent_orders.filter(items__product__category=category)

        order_count = recent_orders.count()

        # Convert to factor (simplified)
        if order_count > 100:
            return 1.2
        elif order_count > 50:
            return 1.1
        elif order_count < 10:
            return 0.9
        else:
            return 1.0

    @staticmethod
    def _generate_demand_pattern(historical_data: List[Dict]) -> Dict:
        """Generate demand pattern from historical data"""
        if not historical_data:
            return {}

        quantities = [d['quantity'] for d in historical_data]

        return {
            'average': np.mean(quantities),
            'peak': np.max(quantities),
            'low': np.min(quantities),
            'variance': np.var(quantities),
            'trend': 'increasing' if len(quantities) > 1 and quantities[-1] > quantities[0] else 'stable'
        }


class RecommendationService:
    """Service for product recommendations"""

    @staticmethod
    def generate_recommendations(user: User, recommendation_type: str = 'hybrid', limit: int = 10) -> List[ProductRecommendation]:
        """Generate product recommendations for a user"""
        try:
            if recommendation_type == 'collaborative':
                return RecommendationService._collaborative_filtering(user, limit)
            elif recommendation_type == 'content_based':
                return RecommendationService._content_based_filtering(user, limit)
            elif recommendation_type == 'trending':
                return RecommendationService._trending_products(user, limit)
            elif recommendation_type == 'location_based':
                return RecommendationService._location_based_recommendations(user, limit)
            else:  # hybrid
                return RecommendationService._hybrid_recommendations(user, limit)

        except Exception as e:
            logger.error(f"Error generating recommendations for {user.email}: {str(e)}")
            return []

    @staticmethod
    def _collaborative_filtering(user: User, limit: int) -> List[ProductRecommendation]:
        """Collaborative filtering recommendations"""
        # Find similar users based on purchase history
        user_orders = user.orders.filter(status__in=['delivered', 'completed'])
        user_products = set(Product.objects.filter(order_items__order__in=user_orders))

        if not user_products:
            return RecommendationService._trending_products(user, limit)

        # Find users with similar purchase patterns
        similar_users = []
        for other_user in User.objects.exclude(id=user.id):
            other_orders = other_user.orders.filter(status__in=['delivered', 'completed'])
            other_products = set(Product.objects.filter(order_items__order__in=other_orders))

            if other_products:
                # Calculate Jaccard similarity
                intersection = len(user_products.intersection(other_products))
                union = len(user_products.union(other_products))
                similarity = intersection / union if union > 0 else 0

                if similarity > 0.1:  # Threshold for similarity
                    similar_users.append((other_user, similarity))

        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)

        # Get recommendations from similar users
        recommended_products = {}
        for similar_user, similarity in similar_users[:10]:  # Top 10 similar users
            similar_user_orders = similar_user.orders.filter(status__in=['delivered', 'completed'])
            similar_user_products = Product.objects.filter(order_items__order__in=similar_user_orders)

            for product in similar_user_products:
                if product not in user_products:  # Don't recommend already purchased products
                    if product.id not in recommended_products:
                        recommended_products[product.id] = {'product': product, 'score': 0, 'similar_users': []}
                    recommended_products[product.id]['score'] += similarity
                    recommended_products[product.id]['similar_users'].append(similar_user.id)

        # Create recommendation objects
        recommendations = []
        sorted_products = sorted(recommended_products.values(), key=lambda x: x['score'], reverse=True)

        for i, item in enumerate(sorted_products[:limit]):
            product = item['product']
            score = min(item['score'], 1.0)  # Normalize score

            recommendation, created = ProductRecommendation.objects.get_or_create(
                user=user,
                product=product,
                recommendation_type='collaborative',
                defaults={
                    'score': Decimal(str(score)),
                    'reason': f"Users with similar preferences also liked this product",
                    'similar_users': item['similar_users'][:5],
                    'user_interaction_history': RecommendationService._get_user_interaction_summary(user)
                }
            )

            if not created:
                recommendation.score = Decimal(str(score))
                recommendation.save()

            recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def _content_based_filtering(user: User, limit: int) -> List[ProductRecommendation]:
        """Content-based filtering recommendations"""
        # Get user's interaction history
        user_interactions = UserInteraction.objects.filter(user=user, product__isnull=False)

        if not user_interactions.exists():
            return RecommendationService._trending_products(user, limit)

        # Analyze user preferences
        liked_categories = {}
        viewed_products = set()

        for interaction in user_interactions:
            if interaction.product:
                viewed_products.add(interaction.product.id)
                category = interaction.product.category

                if category.id not in liked_categories:
                    liked_categories[category.id] = {'category': category, 'score': 0}

                # Weight different interactions
                weight = {
                    'purchase': 5,
                    'add_to_cart': 3,
                    'wishlist': 2,
                    'view': 1,
                    'search': 1
                }.get(interaction.interaction_type, 1)

                liked_categories[category.id]['score'] += weight

        # Find products in preferred categories
        recommended_products = []

        for category_data in sorted(liked_categories.values(), key=lambda x: x['score'], reverse=True):
            category = category_data['category']
            category_products = Product.objects.filter(
                category=category,
                is_active=True
            ).exclude(id__in=viewed_products)[:limit//len(liked_categories) + 1]

            for product in category_products:
                score = min(category_data['score'] / 20, 1.0)  # Normalize score

                recommendation, created = ProductRecommendation.objects.get_or_create(
                    user=user,
                    product=product,
                    recommendation_type='content_based',
                    defaults={
                        'score': Decimal(str(score)),
                        'reason': f"Based on your interest in {category.name}",
                        'product_features': {
                            'category': category.name,
                            'avg_rating': float(product.average_rating or 0),
                            'price_range': 'affordable' if product.price_per_unit < 500 else 'premium'
                        },
                        'user_interaction_history': RecommendationService._get_user_interaction_summary(user)
                    }
                )

                recommended_products.append(recommendation)

                if len(recommended_products) >= limit:
                    break

            if len(recommended_products) >= limit:
                break

        return recommended_products[:limit]

    @staticmethod
    def _trending_products(user: User, limit: int) -> List[ProductRecommendation]:
        """Trending products recommendations"""
        # Calculate trending score based on recent orders and views
        trending_products = Product.objects.filter(
            is_active=True
        ).annotate(
            recent_orders=Count('order_items', filter=Q(order_items__order__created_at__gte=timezone.now() - timedelta(days=7))),
            recent_views=Count('interactions', filter=Q(interactions__created_at__gte=timezone.now() - timedelta(days=7), interactions__interaction_type='view'))
        ).filter(
            Q(recent_orders__gt=0) | Q(recent_views__gt=0)
        ).order_by('-recent_orders', '-recent_views')[:limit]

        recommendations = []
        for i, product in enumerate(trending_products):
            score = max(0.1, 1.0 - (i * 0.1))  # Decreasing score

            recommendation, created = ProductRecommendation.objects.get_or_create(
                user=user,
                product=product,
                recommendation_type='trending',
                defaults={
                    'score': Decimal(str(score)),
                    'reason': "This product is trending in your area",
                    'product_features': {
                        'recent_orders': product.recent_orders,
                        'recent_views': product.recent_views,
                        'trending_rank': i + 1
                    }
                }
            )

            recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def _location_based_recommendations(user: User, limit: int) -> List[ProductRecommendation]:
        """Location-based recommendations"""
        user_profile = getattr(user, 'profile', None)
        if not user_profile or not user_profile.county:
            return RecommendationService._trending_products(user, limit)

        # Find products from farmers in the same region
        local_products = Product.objects.filter(
            farmer__profile__county=user_profile.county,
            is_active=True
        ).order_by('-created_at')[:limit]

        recommendations = []
        for i, product in enumerate(local_products):
            score = max(0.1, 1.0 - (i * 0.05))

            recommendation, created = ProductRecommendation.objects.get_or_create(
                user=user,
                product=product,
                recommendation_type='location_based',
                defaults={
                    'score': Decimal(str(score)),
                    'reason': f"Fresh produce from your county: {user_profile.county}",
                    'product_features': {
                        'farmer_location': product.farmer.profile.county if hasattr(product.farmer, 'profile') else 'Unknown',
                        'distance': 'local'
                    }
                }
            )

            recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def _hybrid_recommendations(user: User, limit: int) -> List[ProductRecommendation]:
        """Hybrid recommendations combining multiple methods"""
        # Get recommendations from different methods
        collaborative = RecommendationService._collaborative_filtering(user, limit//4)
        content_based = RecommendationService._content_based_filtering(user, limit//4)
        trending = RecommendationService._trending_products(user, limit//4)
        location_based = RecommendationService._location_based_recommendations(user, limit//4)

        # Combine and deduplicate
        all_recommendations = collaborative + content_based + trending + location_based
        unique_recommendations = {}

        for rec in all_recommendations:
            if rec.product.id not in unique_recommendations:
                unique_recommendations[rec.product.id] = rec
            else:
                # Update score if higher
                existing = unique_recommendations[rec.product.id]
                if rec.score > existing.score:
                    existing.score = rec.score
                    existing.recommendation_type = 'hybrid'
                    existing.reason = f"Recommended by multiple factors"
                    existing.save()

        return list(unique_recommendations.values())[:limit]

    @staticmethod
    def _get_user_interaction_summary(user: User) -> Dict:
        """Get user interaction summary"""
        interactions = UserInteraction.objects.filter(user=user)
        return {
            'total_views': interactions.filter(interaction_type='view').count(),
            'total_purchases': interactions.filter(interaction_type='purchase').count(),
            'total_searches': interactions.filter(interaction_type='search').count(),
            'last_activity': interactions.first().created_at.isoformat() if interactions.exists() else None
        }

    @staticmethod
    def track_recommendation_interaction(user: User, product: Product, interaction_type: str):
        """Track recommendation effectiveness"""
        try:
            recommendation = ProductRecommendation.objects.filter(
                user=user,
                product=product
            ).first()

            if recommendation:
                now = timezone.now()
                if interaction_type == 'view':
                    recommendation.is_viewed = True
                    recommendation.viewed_at = now
                elif interaction_type == 'click':
                    recommendation.is_clicked = True
                    recommendation.clicked_at = now
                elif interaction_type == 'purchase':
                    recommendation.is_purchased = True

                recommendation.save()

        except Exception as e:
            logger.error(f"Error tracking recommendation interaction: {str(e)}")


class MarketInsightsService:
    """Service for generating market insights"""

    @staticmethod
    def generate_price_trend_insights() -> List[MarketInsight]:
        """Generate price trend insights"""
        insights = []

        # Get products with significant price changes
        recent_predictions = PricePrediction.objects.filter(
            prediction_date__gte=timezone.now().date() - timedelta(days=7)
        )

        for prediction in recent_predictions:
            if abs(prediction.price_change_percentage) > 10:  # Significant change
                trend_direction = "increase" if prediction.price_change_percentage > 0 else "decrease"
                priority = "high" if abs(prediction.price_change_percentage) > 20 else "medium"

                insight = MarketInsight.objects.create(
                    insight_type='price_trend',
                    title=f"{prediction.product.name} Price {trend_direction.title()} Alert",
                    description=f"The price of {prediction.product.name} is predicted to {trend_direction} by {abs(prediction.price_change_percentage):.1f}% in the next {prediction.prediction_horizon.replace('_', ' ')}.",
                    product=prediction.product,
                    key_metrics={
                        'current_price': float(prediction.current_price),
                        'predicted_price': float(prediction.predicted_price),
                        'change_percentage': float(prediction.price_change_percentage),
                        'confidence': float(prediction.confidence_score)
                    },
                    target_roles=['farmer', 'buyer'],
                    priority=priority,
                    recommendations=[
                        f"Farmers: Consider {'holding inventory' if trend_direction == 'increase' else 'selling current stock'} to maximize profits",
                        f"Buyers: Consider {'purchasing now' if trend_direction == 'increase' else 'waiting for better prices'} based on this trend"
                    ]
                )

                insights.append(insight)

        return insights

    @staticmethod
    def generate_demand_supply_insights() -> List[MarketInsight]:
        """Generate supply and demand insights"""
        insights = []

        # Analyze demand forecasts
        recent_forecasts = DemandForecast.objects.filter(
            forecast_date__gte=timezone.now().date() - timedelta(days=7)
        )

        for forecast in recent_forecasts:
            if abs(forecast.demand_change_percentage) > 15:  # Significant demand change
                change_type = "surge" if forecast.demand_change_percentage > 0 else "drop"

                insight = MarketInsight.objects.create(
                    insight_type='supply_demand',
                    title=f"Demand {change_type.title()} Alert: {forecast.product.name if forecast.product else forecast.category.name}",
                    description=f"Demand is forecasted to {change_type} by {abs(forecast.demand_change_percentage):.1f}% for {forecast.product.name if forecast.product else forecast.category.name + ' category'}.",
                    product=forecast.product,
                    category=forecast.category,
                    region=forecast.region,
                    key_metrics={
                        'predicted_demand': float(forecast.predicted_demand_quantity),
                        'demand_change': float(forecast.demand_change_percentage),
                        'confidence': float(forecast.confidence_score)
                    },
                    target_roles=['farmer', 'buyer', 'cooperative'],
                    priority="high" if abs(forecast.demand_change_percentage) > 25 else "medium",
                    recommendations=[
                        f"Farmers: {'Increase production' if change_type == 'surge' else 'Diversify crops'} to capitalize on market conditions",
                        f"Buyers: {'Secure supply early' if change_type == 'surge' else 'Negotiate better prices'} given the demand forecast"
                    ]
                )

                insights.append(insight)

        return insights

    @staticmethod
    def generate_seasonal_insights() -> List[MarketInsight]:
        """Generate seasonal pattern insights"""
        insights = []
        current_month = datetime.now().month

        # Seasonal advice for different product categories
        seasonal_advice = {
            1: {"vegetables": "Peak season for leafy greens", "fruits": "Citrus fruits in season"},
            2: {"vegetables": "Good time for root vegetables", "fruits": "Late citrus harvest"},
            3: {"vegetables": "Start summer crop preparation", "fruits": "Transition to tropical fruits"},
            4: {"vegetables": "Peak planting season", "fruits": "Mango season begins"},
            5: {"vegetables": "Harvest winter crops", "fruits": "Peak mango season"},
            6: {"vegetables": "Dry season crops", "fruits": "Avocado season"},
            7: {"vegetables": "Hardy vegetables thrive", "fruits": "Passion fruit season"},
            8: {"vegetables": "Prepare for planting season", "fruits": "Late tropical fruits"},
            9: {"vegetables": "Short rains planting", "fruits": "Early harvest season"},
            10: {"vegetables": "Rapid growth period", "fruits": "Banana peak season"},
            11: {"vegetables": "Harvest season begins", "fruits": "Diverse fruit availability"},
            12: {"vegetables": "Peak harvest season", "fruits": "End of year harvest"}
        }

        if current_month in seasonal_advice:
            advice = seasonal_advice[current_month]

            for category_name, description in advice.items():
                try:
                    category = ProductCategory.objects.filter(name__icontains=category_name).first()
                    if category:
                        insight = MarketInsight.objects.create(
                            insight_type='seasonal_pattern',
                            title=f"Seasonal Insight: {category.name}",
                            description=description,
                            category=category,
                            key_metrics={
                                'month': current_month,
                                'season_factor': 1.2 if 'peak' in description.lower() else 1.0
                            },
                            target_roles=['farmer'],
                            priority='medium',
                            recommendations=[
                                f"Focus on {category.name} production this month",
                                "Plan ahead for next season's planting",
                                "Consider value-added processing opportunities"
                            ]
                        )
                        insights.append(insight)
                except Exception as e:
                    logger.error(f"Error creating seasonal insight: {str(e)}")

        return insights

    @staticmethod
    def generate_opportunity_alerts() -> List[MarketInsight]:
        """Generate market opportunity alerts"""
        insights = []

        # Find products with low supply but high demand
        high_demand_products = Product.objects.annotate(
            recent_orders=Count('order_items', filter=Q(order_items__order__created_at__gte=timezone.now() - timedelta(days=30))),
            recent_supply=Count('id', filter=Q(quantity_available__gt=0))
        ).filter(recent_orders__gt=10, recent_supply__lt=5)

        for product in high_demand_products:
            insight = MarketInsight.objects.create(
                insight_type='opportunity_alert',
                title=f"Market Opportunity: {product.name}",
                description=f"High demand but low supply detected for {product.name}. This presents a good opportunity for farmers.",
                product=product,
                key_metrics={
                    'recent_orders': product.recent_orders,
                    'available_supply': product.recent_supply,
                    'demand_supply_ratio': product.recent_orders / max(product.recent_supply, 1)
                },
                target_roles=['farmer', 'cooperative'],
                priority='high',
                recommendations=[
                    f"Consider increasing {product.name} production",
                    "Coordinate with other farmers for consistent supply",
                    "Explore premium pricing opportunities"
                ]
            )
            insights.append(insight)

        return insights


# Utility functions for easy integration
def track_user_interaction(user: User, interaction_type: str, product: Product = None, **kwargs):
    """Track user interaction for recommendation system"""
    try:
        UserInteraction.objects.create(
            user=user,
            product=product,
            interaction_type=interaction_type,
            search_query=kwargs.get('search_query'),
            session_id=kwargs.get('session_id'),
            duration=kwargs.get('duration'),
            referrer=kwargs.get('referrer'),
            user_agent=kwargs.get('user_agent'),
            ip_address=kwargs.get('ip_address'),
            device_type=kwargs.get('device_type'),
            metadata=kwargs.get('metadata', {})
        )
    except Exception as e:
        logger.error(f"Error tracking user interaction: {str(e)}")


def update_ai_model_metrics(model_type: str, model_version: str, metrics: Dict):
    """Update AI model performance metrics"""
    try:
        model_metrics, created = AIModelMetrics.objects.get_or_create(
            model_type=model_type,
            model_version=model_version,
            defaults={
                'training_date': timezone.now(),
                'training_data_size': metrics.get('training_data_size', 0),
                'features_count': metrics.get('features_count', 0),
                'parameters': metrics.get('parameters', {}),
                'accuracy': metrics.get('accuracy'),
                'precision': metrics.get('precision'),
                'recall': metrics.get('recall'),
                'f1_score': metrics.get('f1_score'),
                'mae': metrics.get('mae'),
                'mse': metrics.get('mse'),
                'avg_response_time': metrics.get('avg_response_time')
            }
        )

        if not created:
            # Update existing metrics
            for key, value in metrics.items():
                if hasattr(model_metrics, key) and value is not None:
                    setattr(model_metrics, key, value)
            model_metrics.save()

        return model_metrics

    except Exception as e:
        logger.error(f"Error updating AI model metrics: {str(e)}")
        return None