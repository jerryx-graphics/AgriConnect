from django.contrib import admin
from .models import (
    Order, OrderItem, Cart, CartItem, OrderTracking,
    DeliveryRequest, Invoice
)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'buyer', 'status', 'payment_status', 'total_amount',
        'delivery_county', 'items_count', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'delivery_county', 'created_at',
        'confirmed_at', 'delivered_at'
    ]
    search_fields = ['order_id', 'buyer__first_name', 'buyer__last_name', 'buyer__email']
    readonly_fields = ['order_id', 'items_count', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderTrackingInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'buyer', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'platform_fee', 'total_amount')
        }),
        ('Delivery Information', {
            'fields': (
                'delivery_address', 'delivery_county', 'delivery_sub_county',
                'delivery_latitude', 'delivery_longitude', 'delivery_phone', 'delivery_notes'
            )
        }),
        ('Timestamps', {
            'fields': (
                'expected_delivery_date', 'confirmed_at', 'delivered_at',
                'cancelled_at', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Ratings & Feedback', {
            'fields': ('buyer_rating', 'buyer_feedback', 'farmer_rating', 'farmer_feedback'),
            'classes': ('collapse',)
        }),
    )

    def items_count(self, obj):
        return obj.items_count
    items_count.short_description = 'Items Count'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['order__order_id', 'product__name']
    readonly_fields = ['total_price', 'created_at', 'updated_at']

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['unit_price', 'total_price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'total_amount', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['items_count', 'total_amount', 'created_at', 'updated_at']
    inlines = [CartItemInline]

    def items_count(self, obj):
        return obj.items_count
    items_count.short_description = 'Items Count'

    def total_amount(self, obj):
        return f"KES {obj.total_amount:,.2f}"
    total_amount.short_description = 'Total Amount'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['cart__user__first_name', 'cart__user__last_name', 'product__name']
    readonly_fields = ['unit_price', 'total_price', 'created_at', 'updated_at']

@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'location', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id', 'message', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'transporter', 'pickup_county', 'status',
        'delivery_distance', 'estimated_cost', 'created_at'
    ]
    list_filter = [
        'status', 'pickup_county', 'requires_refrigeration',
        'requires_careful_handling', 'created_at'
    ]
    search_fields = [
        'order__order_id', 'transporter__first_name', 'transporter__last_name',
        'pickup_address'
    ]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Order & Transporter', {
            'fields': ('order', 'transporter', 'status')
        }),
        ('Pickup Information', {
            'fields': (
                'pickup_address', 'pickup_county', 'pickup_latitude',
                'pickup_longitude', 'pickup_contact'
            )
        }),
        ('Delivery Details', {
            'fields': (
                'delivery_distance', 'estimated_cost', 'actual_cost',
                'weight_estimate'
            )
        }),
        ('Special Requirements', {
            'fields': ('requires_refrigeration', 'requires_careful_handling')
        }),
        ('Timestamps', {
            'fields': (
                'accepted_at', 'picked_up_at', 'delivered_at',
                'cancelled_at', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'order', 'total_amount', 'is_paid',
        'issued_at', 'due_date'
    ]
    list_filter = ['is_paid', 'issued_at', 'due_date']
    search_fields = ['invoice_number', 'order__order_id']
    readonly_fields = ['invoice_number', 'issued_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'issued_at', 'due_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'delivery_fee', 'platform_fee', 'tax_amount', 'total_amount')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
