from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import (
    Order, OrderItem, Cart, CartItem, OrderTracking,
    DeliveryRequest, Invoice
)
from products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'unit_price', 'total_price', 'created_at'
        ]
        read_only_fields = ['unit_price', 'total_price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')

        try:
            from products.models import Product
            product = Product.objects.get(id=product_id, is_available=True, is_deleted=False)

            if quantity < product.minimum_order:
                raise serializers.ValidationError(
                    f"Minimum order quantity is {product.minimum_order} {product.unit}"
                )

            if quantity > product.quantity_available:
                raise serializers.ValidationError(
                    f"Only {product.quantity_available} {product.unit} available"
                )

            attrs['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or unavailable")

        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'items_count', 'total_amount', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    farmer_name = serializers.CharField(source='product.farmer.full_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'farmer_name', 'quantity', 'unit_price',
            'total_price', 'special_instructions', 'created_at'
        ]

class OrderTrackingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)

    class Meta:
        model = OrderTracking
        fields = [
            'id', 'status', 'message', 'location', 'latitude', 'longitude',
            'updated_by_name', 'created_at'
        ]

class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.ReadOnlyField()
    farmers = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'status', 'payment_status', 'total_amount',
            'delivery_county', 'expected_delivery_date', 'items_count',
            'farmers', 'created_at'
        ]

    def get_farmers(self, obj):
        farmers = obj.farmers
        return [{'name': farmer.full_name, 'phone': farmer.phone_number} for farmer in farmers]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(many=True, read_only=True)
    items_count = serializers.ReadOnlyField()
    farmers = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'status', 'payment_status', 'subtotal',
            'delivery_fee', 'platform_fee', 'total_amount', 'delivery_address',
            'delivery_county', 'delivery_sub_county', 'delivery_phone',
            'delivery_notes', 'expected_delivery_date', 'confirmed_at',
            'delivered_at', 'buyer_rating', 'buyer_feedback',
            'farmer_rating', 'farmer_feedback', 'items', 'tracking',
            'items_count', 'farmers', 'created_at', 'updated_at'
        ]

    def get_farmers(self, obj):
        farmers = obj.farmers
        return [{'name': farmer.full_name, 'phone': farmer.phone_number} for farmer in farmers]

class OrderCreateSerializer(serializers.ModelSerializer):
    cart_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of cart items with product_id, quantity, and special_instructions"
    )

    class Meta:
        model = Order
        fields = [
            'delivery_address', 'delivery_county', 'delivery_sub_county',
            'delivery_latitude', 'delivery_longitude', 'delivery_phone',
            'delivery_notes', 'cart_items'
        ]

    def validate_cart_items(self, value):
        if not value:
            raise serializers.ValidationError("Cart cannot be empty")

        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each cart item must have product_id and quantity"
                )

        return value

    @transaction.atomic
    def create(self, validated_data):
        cart_items_data = validated_data.pop('cart_items')
        user = self.context['request'].user

        # Create order
        order = Order.objects.create(buyer=user, **validated_data)

        # Create order items
        from products.models import Product
        total_subtotal = 0

        for item_data in cart_items_data:
            try:
                product = Product.objects.get(
                    id=item_data['product_id'],
                    is_available=True,
                    is_deleted=False
                )

                quantity = float(item_data['quantity'])

                # Validate quantity
                if quantity < product.minimum_order:
                    raise serializers.ValidationError(
                        f"Minimum order for {product.name} is {product.minimum_order} {product.unit}"
                    )

                if quantity > product.quantity_available:
                    raise serializers.ValidationError(
                        f"Only {product.quantity_available} {product.unit} available for {product.name}"
                    )

                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price_per_unit,
                    special_instructions=item_data.get('special_instructions', '')
                )

                total_subtotal += order_item.total_price

                # Update product quantity
                product.quantity_available -= quantity
                product.save()

                # Update product analytics
                analytics, created = product.analytics.get_or_create(product=product)
                analytics.orders_count += 1
                analytics.last_ordered = timezone.now()
                analytics.save()

            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product {item_data['product_id']} not found")

        # Calculate order totals
        order.subtotal = total_subtotal
        order.calculate_totals()

        # Create initial tracking
        OrderTracking.objects.create(
            order=order,
            status='order_placed',
            message='Order has been placed successfully',
            updated_by=user
        )

        # Clear user's cart
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

        return order

class DeliveryRequestSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    buyer_name = serializers.CharField(source='order.buyer.full_name', read_only=True)
    transporter_name = serializers.CharField(source='transporter.full_name', read_only=True)

    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'order_id', 'buyer_name', 'transporter_name', 'pickup_address',
            'pickup_county', 'pickup_contact', 'delivery_distance', 'estimated_cost',
            'actual_cost', 'status', 'requires_refrigeration', 'requires_careful_handling',
            'weight_estimate', 'accepted_at', 'picked_up_at', 'delivered_at',
            'created_at'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    buyer_name = serializers.CharField(source='order.buyer.full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'order_id', 'buyer_name', 'invoice_number', 'issued_at',
            'due_date', 'subtotal', 'delivery_fee', 'platform_fee',
            'tax_amount', 'total_amount', 'is_paid', 'paid_at'
        ]

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    message = serializers.CharField(max_length=500)
    location = serializers.CharField(max_length=200, required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)

class OrderRatingSerializer(serializers.Serializer):
    buyer_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    buyer_feedback = serializers.CharField(max_length=1000, required=False)
    farmer_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    farmer_feedback = serializers.CharField(max_length=1000, required=False)