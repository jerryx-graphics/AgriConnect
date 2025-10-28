from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, UserProfile, FarmerProfile, BuyerProfile,
    TransporterProfile, PhoneVerification, EmailVerification
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_phone_verified', 'is_email_verified', 'verification_status', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('AgriConnect Fields', {
            'fields': ('phone_number', 'role', 'is_phone_verified', 'is_email_verified',
                      'verification_status', 'profile_picture', 'date_of_birth')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('AgriConnect Fields', {
            'fields': ('email', 'phone_number', 'role', 'first_name', 'last_name')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'county', 'sub_county', 'created_at']
    list_filter = ['county', 'sub_county', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'national_id']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'farm_name', 'farm_size', 'farming_type', 'years_of_experience']
    list_filter = ['farming_type', 'years_of_experience', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'farm_name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'buyer_type', 'company_name', 'average_order_value']
    list_filter = ['buyer_type', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company_name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(TransporterProfile)
class TransporterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'vehicle_registration', 'vehicle_capacity', 'rate_per_km']
    list_filter = ['vehicle_type', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'vehicle_registration', 'license_number']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_verified', 'expires_at', 'created_at']
    list_filter = ['is_verified', 'created_at', 'expires_at']
    search_fields = ['user__email', 'phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'is_verified', 'expires_at', 'created_at']
    list_filter = ['is_verified', 'created_at', 'expires_at']
    search_fields = ['user__email', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
