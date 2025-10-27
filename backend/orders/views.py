from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.utils import APIResponse
from .models import (
    Order, OrderItem, Cart, CartItem, OrderTracking,
    DeliveryRequest, Invoice
)
from .serializers import (
    CartSerializer, CartItemSerializer, OrderListSerializer,
    OrderDetailSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderRatingSerializer, DeliveryRequestSerializer, InvoiceSerializer
)

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

@extend_schema(
    tags=['Orders'],
    summary='Add item to cart',
    description='''
    Add a product to the user's shopping cart. If the product already exists in the cart,
    the quantity will be increased by the specified amount.

    **Validation:**
    - Product must be available and not deleted
    - Quantity must meet minimum order requirements
    - Quantity must not exceed available stock
    ''',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'string', 'format': 'uuid', 'description': 'Product UUID'},
                'quantity': {'type': 'number', 'description': 'Quantity to add to cart'}
            },
            'required': ['product_id', 'quantity']
        }
    },
    responses={
        201: OpenApiResponse(description='Item added to cart successfully'),
        200: OpenApiResponse(description='Item quantity updated in cart'),
        400: OpenApiResponse(description='Validation error - invalid product or quantity')
    },
    examples=[
        OpenApiExample(
            'Add to Cart Request',
            value={
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "quantity": 5.0
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            APIResponse.success(
                CartItemSerializer(cart_item).data,
                "Item added to cart successfully"
            ),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    return Response(
        APIResponse.error("Failed to add item to cart", serializer.errors),
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user,
            is_deleted=False
        )
    except CartItem.DoesNotExist:
        return Response(
            APIResponse.error("Cart item not found"),
            status=status.HTTP_404_NOT_FOUND
        )

    quantity = request.data.get('quantity')
    if not quantity or float(quantity) <= 0:
        return Response(
            APIResponse.error("Invalid quantity"),
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate quantity against product availability
    if float(quantity) > cart_item.product.quantity_available:
        return Response(
            APIResponse.error(
                f"Only {cart_item.product.quantity_available} {cart_item.product.unit} available"
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    cart_item.quantity = quantity
    cart_item.save()

    return Response(
        APIResponse.success(
            CartItemSerializer(cart_item).data,
            "Cart item updated successfully"
        )
    )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=request.user,
            is_deleted=False
        )
        cart_item.is_deleted = True
        cart_item.deleted_at = timezone.now()
        cart_item.save()

        return Response(
            APIResponse.success(message="Item removed from cart"),
            status=status.HTTP_204_NO_CONTENT
        )
    except CartItem.DoesNotExist:
        return Response(
            APIResponse.error("Cart item not found"),
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.update(is_deleted=True, deleted_at=timezone.now())

        return Response(
            APIResponse.success(message="Cart cleared successfully"),
            status=status.HTTP_204_NO_CONTENT
        )
    except Cart.DoesNotExist:
        return Response(
            APIResponse.success(message="Cart is already empty"),
            status=status.HTTP_200_OK
        )

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['buyer', 'admin']:
            return Response(
                APIResponse.error("Only buyers can create orders"),
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                APIResponse.success(
                    OrderDetailSerializer(order, context={'request': request}).data,
                    "Order created successfully"
                ),
                status=status.HTTP_201_CREATED
            )

        return Response(
            APIResponse.error("Order creation failed", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'buyer':
            return Order.objects.filter(buyer=user, is_deleted=False)
        elif user.role == 'farmer':
            return Order.objects.filter(
                items__product__farmer=user,
                is_deleted=False
            ).distinct()
        elif user.role == 'admin':
            return Order.objects.filter(is_deleted=False)
        else:
            return Order.objects.none()

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'buyer':
            return Order.objects.filter(buyer=user, is_deleted=False)
        elif user.role == 'farmer':
            return Order.objects.filter(
                items__product__farmer=user,
                is_deleted=False
            ).distinct()
        elif user.role == 'admin':
            return Order.objects.filter(is_deleted=False)
        else:
            return Order.objects.none()

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, order_id):
    try:
        user = request.user
        if user.role == 'buyer':
            order = Order.objects.get(id=order_id, buyer=user, is_deleted=False)
        elif user.role == 'farmer':
            order = Order.objects.filter(
                id=order_id,
                items__product__farmer=user,
                is_deleted=False
            ).distinct().first()
            if not order:
                raise Order.DoesNotExist
        elif user.role == 'admin':
            order = Order.objects.get(id=order_id, is_deleted=False)
        else:
            return Response(
                APIResponse.error("Permission denied"),
                status=status.HTTP_403_FORBIDDEN
            )

    except Order.DoesNotExist:
        return Response(
            APIResponse.error("Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OrderStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        new_status = serializer.validated_data['status']
        message = serializer.validated_data['message']
        location = serializer.validated_data.get('location')
        latitude = serializer.validated_data.get('latitude')
        longitude = serializer.validated_data.get('longitude')

        # Update order status
        old_status = order.status
        order.status = new_status

        # Update timestamps based on status
        if new_status == 'confirmed' and old_status != 'confirmed':
            order.confirmed_at = timezone.now()
        elif new_status == 'delivered' and old_status != 'delivered':
            order.delivered_at = timezone.now()
        elif new_status == 'cancelled' and old_status != 'cancelled':
            order.cancelled_at = timezone.now()

        order.save()

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status=new_status,
            message=message,
            location=location,
            latitude=latitude,
            longitude=longitude,
            updated_by=user
        )

        return Response(
            APIResponse.success(
                OrderDetailSerializer(order, context={'request': request}).data,
                "Order status updated successfully"
            )
        )

    return Response(
        APIResponse.error("Invalid data", serializer.errors),
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, buyer=request.user, is_deleted=False)

        if order.status in ['delivered', 'completed', 'cancelled']:
            return Response(
                APIResponse.error("Order cannot be cancelled at this stage"),
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update order status
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save()

        # Restore product quantities
        for item in order.items.all():
            item.product.quantity_available += item.quantity
            item.product.save()

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            message=request.data.get('reason', 'Order cancelled by buyer'),
            updated_by=request.user
        )

        return Response(
            APIResponse.success(message="Order cancelled successfully")
        )

    except Order.DoesNotExist:
        return Response(
            APIResponse.error("Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, buyer=request.user, is_deleted=False)

        if order.status != 'completed':
            return Response(
                APIResponse.error("Order must be completed before rating"),
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderRatingSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            if 'buyer_rating' in data:
                order.buyer_rating = data['buyer_rating']
            if 'buyer_feedback' in data:
                order.buyer_feedback = data['buyer_feedback']
            if 'farmer_rating' in data:
                order.farmer_rating = data['farmer_rating']
            if 'farmer_feedback' in data:
                order.farmer_feedback = data['farmer_feedback']

            order.save()

            return Response(
                APIResponse.success(message="Rating submitted successfully")
            )

        return Response(
            APIResponse.error("Invalid rating data", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    except Order.DoesNotExist:
        return Response(
            APIResponse.error("Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )

class DeliveryRequestListView(generics.ListAPIView):
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'pickup_county']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'transporter':
            return DeliveryRequest.objects.filter(
                status='pending',
                is_deleted=False
            )
        elif user.role in ['farmer', 'buyer']:
            return DeliveryRequest.objects.filter(
                order__buyer=user,
                is_deleted=False
            )
        elif user.role == 'admin':
            return DeliveryRequest.objects.filter(is_deleted=False)
        else:
            return DeliveryRequest.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_delivery_request(request, delivery_id):
    if request.user.role != 'transporter':
        return Response(
            APIResponse.error("Only transporters can accept delivery requests"),
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        delivery_request = DeliveryRequest.objects.get(
            id=delivery_id,
            status='pending',
            is_deleted=False
        )

        delivery_request.transporter = request.user
        delivery_request.status = 'accepted'
        delivery_request.accepted_at = timezone.now()
        delivery_request.save()

        # Update order status
        order = delivery_request.order
        order.status = 'in_transit'
        order.save()

        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='picked_up',
            message=f"Order picked up by {request.user.full_name}",
            updated_by=request.user
        )

        return Response(
            APIResponse.success(
                DeliveryRequestSerializer(delivery_request).data,
                "Delivery request accepted successfully"
            )
        )

    except DeliveryRequest.DoesNotExist:
        return Response(
            APIResponse.error("Delivery request not found"),
            status=status.HTTP_404_NOT_FOUND
        )
