from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class ProductCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name

class Product(BaseModel):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('ton', 'Ton'),
        ('piece', 'Piece'),
        ('dozen', 'Dozen'),
        ('bag', 'Bag'),
        ('crate', 'Crate'),
        ('liter', 'Liter'),
        ('ml', 'Milliliter'),
    ]

    CONDITION_CHOICES = [
        ('fresh', 'Fresh'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('dried', 'Dried'),
        ('processed', 'Processed'),
    ]

    QUALITY_CHOICES = [
        ('premium', 'Premium'),
        ('standard', 'Standard'),
        ('economic', 'Economic'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    # Product attributes
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='fresh')
    quality_grade = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='standard')
    harvest_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    # Location
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Certifications and attributes
    is_organic = models.BooleanField(default=False)
    certifications = models.JSONField(default=list, help_text="List of certifications")

    # Product status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # SEO and search
    tags = models.JSONField(default=list, help_text="Search tags for the product")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farmer', 'category']),
            models.Index(fields=['county', 'is_available']),
            models.Index(fields=['price_per_unit']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} by {self.farmer.full_name}"

    @property
    def total_value(self) -> float:
        return self.price_per_unit * self.quantity_available

    @property
    def is_in_stock(self) -> bool:
        return self.quantity_available > 0 and self.is_available

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        unique_together = ['product', 'buyer']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.name} by {self.buyer.full_name}"

class ProductPriceHistory(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    date_changed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_changed']

    def __str__(self):
        return f"Price history for {self.product.name}"

class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.full_name}'s wishlist: {self.product.name}"

class ProductAnalytics(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analytics')
    views_count = models.PositiveIntegerField(default=0)
    inquiries_count = models.PositiveIntegerField(default=0)
    orders_count = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    last_ordered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Analytics for {self.product.name}"
