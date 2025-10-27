from rest_framework import serializers
from django.db import transaction
from .models import (
    ProductCategory, Product, ProductImage, ProductReview,
    ProductPriceHistory, Wishlist, ProductAnalytics
)

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'image', 'is_active', 'created_at']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'caption', 'created_at']

class ProductReviewSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    buyer_avatar = serializers.ImageField(source='buyer.profile_picture', read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            'id', 'rating', 'comment', 'is_verified_purchase',
            'created_at', 'buyer_name', 'buyer_avatar'
        ]
        read_only_fields = ['buyer_name', 'buyer_avatar', 'is_verified_purchase']

class ProductListSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price_per_unit', 'unit',
            'quantity_available', 'minimum_order', 'condition', 'quality_grade',
            'county', 'sub_county', 'is_organic', 'is_available', 'is_featured',
            'farmer_name', 'category_name', 'primary_image', 'average_rating',
            'review_count', 'distance', 'created_at'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_distance(self, obj):
        # This would be calculated based on user's location in the view
        return self.context.get('distance', None)

class ProductDetailSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)
    farmer_avatar = serializers.ImageField(source='farmer.profile_picture', read_only=True)
    farmer_phone = serializers.CharField(source='farmer.phone_number', read_only=True)
    category = ProductCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    total_value = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price_per_unit', 'unit',
            'quantity_available', 'minimum_order', 'condition', 'quality_grade',
            'harvest_date', 'expiry_date', 'county', 'sub_county', 'ward',
            'latitude', 'longitude', 'is_organic', 'certifications',
            'is_available', 'is_featured', 'tags', 'total_value', 'is_in_stock',
            'farmer_name', 'farmer_avatar', 'farmer_phone', 'category',
            'images', 'reviews', 'average_rating', 'review_count',
            'is_wishlisted', 'created_at', 'updated_at'
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price_per_unit', 'unit',
            'quantity_available', 'minimum_order', 'condition', 'quality_grade',
            'harvest_date', 'expiry_date', 'county', 'sub_county', 'ward',
            'latitude', 'longitude', 'is_organic', 'certifications',
            'is_available', 'tags', 'images', 'uploaded_images'
        ]

    def validate_price_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity_available(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    @transaction.atomic
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(farmer=self.context['request'].user, **validated_data)

        # Handle price history
        ProductPriceHistory.objects.create(
            product=product,
            price_per_unit=product.price_per_unit
        )

        # Handle image uploads
        for i, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(i == 0)  # First image is primary
            )

        # Create analytics record
        ProductAnalytics.objects.create(product=product)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        old_price = instance.price_per_unit
        new_price = validated_data.get('price_per_unit', old_price)

        # Update product
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Track price changes
        if old_price != new_price:
            ProductPriceHistory.objects.create(
                product=instance,
                price_per_unit=new_price
            )

        # Handle new image uploads
        if uploaded_images:
            existing_images_count = instance.images.count()
            for i, image in enumerate(uploaded_images):
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    is_primary=(existing_images_count == 0 and i == 0)
                )

        return instance

class ProductReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']

class ProductAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAnalytics
        fields = [
            'views_count', 'inquiries_count', 'orders_count',
            'total_revenue', 'last_viewed', 'last_ordered'
        ]