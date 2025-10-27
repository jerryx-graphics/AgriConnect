from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from core.models import BaseModel

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('transporter', 'Transporter'),
        ('cooperative', 'Cooperative'),
        ('admin', 'Admin'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+254[17]\d{8}$',
        message="Phone number must be in format: '+254712345678'"
    )

    email = models.EmailField(unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_verified(self) -> bool:
        return self.is_phone_verified and self.is_email_verified and self.verification_status == 'verified'

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    sub_county = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)

    # KYC Documents
    national_id_front = models.ImageField(upload_to='kyc/national_id/', null=True, blank=True)
    national_id_back = models.ImageField(upload_to='kyc/national_id/', null=True, blank=True)
    certificate_of_incorporation = models.FileField(upload_to='kyc/certificates/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

class FarmerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200, null=True, blank=True)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Farm size in acres")

    FARMING_TYPE_CHOICES = [
        ('organic', 'Organic'),
        ('conventional', 'Conventional'),
        ('mixed', 'Mixed'),
    ]
    farming_type = models.CharField(max_length=20, choices=FARMING_TYPE_CHOICES, default='conventional')

    main_crops = models.JSONField(default=list, help_text="List of main crops grown")
    years_of_experience = models.PositiveIntegerField(default=0)
    certifications = models.JSONField(default=list, help_text="List of farming certifications")

    # Banking details for payments
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Farmer: {self.user.full_name}"

class BuyerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')

    BUYER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('retail', 'Retail Business'),
        ('wholesale', 'Wholesale Business'),
        ('export', 'Export Business'),
        ('processing', 'Processing Company'),
    ]
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES, default='individual')

    company_name = models.CharField(max_length=200, null=True, blank=True)
    business_registration = models.CharField(max_length=100, null=True, blank=True)
    preferred_products = models.JSONField(default=list, help_text="List of preferred product categories")
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Buyer: {self.user.full_name}"

class TransporterProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='transporter_profile')

    VEHICLE_TYPE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('lorry', 'Lorry'),
    ]

    company_name = models.CharField(max_length=200, null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    vehicle_registration = models.CharField(max_length=20, unique=True)
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity in tons")
    license_number = models.CharField(max_length=50, unique=True)
    insurance_number = models.CharField(max_length=100, null=True, blank=True)
    service_areas = models.JSONField(default=list, help_text="List of counties/areas served")
    rate_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Transporter: {self.user.full_name}"

class PhoneVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ['user', 'phone_number']

    def __str__(self):
        return f"Phone verification for {self.user.email}"

class EmailVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    verification_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Email verification for {self.user.email}"
