from django.contrib import admin
from .models import (
    ProductCategory, Product, ProductImage, ProductReview,
    ProductPriceHistory, Wishlist, ProductAnalytics
)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['id', 'created_at']

class ProductAnalyticsInline(admin.StackedInline):
    model = ProductAnalytics
    readonly_fields = ['views_count', 'inquiries_count', 'orders_count', 'total_revenue', 'last_viewed', 'last_ordered']
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'farmer', 'category', 'price_per_unit', 'unit',
        'quantity_available', 'county', 'is_available', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'county', 'condition', 'quality_grade',
        'is_organic', 'is_available', 'is_featured', 'created_at'
    ]
    search_fields = ['name', 'description', 'farmer__first_name', 'farmer__last_name', 'farmer__email']
    readonly_fields = ['id', 'total_value', 'is_in_stock', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductAnalyticsInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'category', 'name', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price_per_unit', 'unit', 'quantity_available', 'minimum_order')
        }),
        ('Product Details', {
            'fields': ('condition', 'quality_grade', 'harvest_date', 'expiry_date', 'is_organic', 'certifications')
        }),
        ('Location', {
            'fields': ('county', 'sub_county', 'ward', 'latitude', 'longitude')
        }),
        ('Status & Marketing', {
            'fields': ('is_available', 'is_featured', 'tags')
        }),
        ('Calculated Fields', {
            'fields': ('total_value', 'is_in_stock'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'caption', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'caption']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'buyer', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'buyer__first_name', 'buyer__last_name', 'comment']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'price_per_unit', 'date_changed']
    list_filter = ['date_changed']
    search_fields = ['product__name']
    readonly_fields = ['id', 'date_changed', 'created_at', 'updated_at']
    ordering = ['-date_changed']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'views_count', 'inquiries_count', 'orders_count', 'total_revenue']
    list_filter = ['last_viewed', 'last_ordered']
    search_fields = ['product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
