from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from core.models import BaseModel
from core.utils import generate_order_id
from products.models import Product

User = get_user_model()

class Order(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order_id = models.CharField(max_length=20, unique=True, default=generate_order_id)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Delivery information
    delivery_address = models.TextField()
    delivery_county = models.CharField(max_length=100)
    delivery_sub_county = models.CharField(max_length=100, null=True, blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_phone = models.CharField(max_length=15)
    delivery_notes = models.TextField(null=True, blank=True)

    # Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)

    # Ratings and feedback
    buyer_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    buyer_feedback = models.TextField(null=True, blank=True)
    farmer_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    farmer_feedback = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['order_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_id} by {self.buyer.full_name}"

    def calculate_totals(self):
        self.subtotal = sum(item.total_price for item in self.items.all())

        # Calculate platform fee (2-5% of subtotal)
        platform_fee_rate = Decimal('0.03')  # 3%
        self.platform_fee = self.subtotal * platform_fee_rate

        self.total_amount = self.subtotal + self.delivery_fee + self.platform_fee
        self.save()

    @property
    def farmers(self):
        return User.objects.filter(products__orderitem__order=self).distinct()

    @property
    def items_count(self):
        return self.items.count()

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Special requests
    special_instructions = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity} {self.product.unit} of {self.product.name}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart for {self.user.full_name}"

    @property
    def items_count(self):
        return self.items.count()

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} {self.product.unit} of {self.product.name} in cart"

    def save(self, *args, **kwargs):
        self.unit_price = self.product.price_per_unit
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class OrderTracking(BaseModel):
    STATUS_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('farmer_confirmed', 'Farmer Confirmed'),
        ('payment_received', 'Payment Received'),
        ('preparing_order', 'Preparing Order'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    message = models.TextField()
    location = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracking_updates')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tracking update for {self.order.order_id}: {self.status}"

class DeliveryRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_request')
    transporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_requests',
        null=True,
        blank=True
    )
    pickup_address = models.TextField()
    pickup_county = models.CharField(max_length=100)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_contact = models.CharField(max_length=15)

    delivery_distance = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in KM
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Special delivery requirements
    requires_refrigeration = models.BooleanField(default=False)
    requires_careful_handling = models.BooleanField(default=False)
    weight_estimate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in KG

    # Timestamps
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery request for {self.order.order_id}"

class Invoice(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

    # Invoice details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.order.order_id}"

    def generate_invoice_number(self):
        from datetime import datetime
        return f"INV-{datetime.now().strftime('%Y%m%d')}-{self.order.order_id}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
