from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import string
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.utils import generate_random_string, send_notification_email, APIResponse
from .models import (
    User, UserProfile, FarmerProfile, BuyerProfile,
    TransporterProfile, PhoneVerification, EmailVerification
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserProfileSerializer,
    FarmerProfileSerializer, BuyerProfileSerializer, TransporterProfileSerializer,
    PhoneVerificationSerializer, PhoneVerificationConfirmSerializer,
    EmailVerificationSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
)

@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='''
    Register a new user with role-based access. Available roles:
    - farmer: Agricultural producers
    - buyer: Product purchasers (individuals or businesses)
    - transporter: Delivery service providers
    - cooperative: Agricultural cooperatives
    - admin: Platform administrators

    Upon successful registration, the user receives JWT tokens and appropriate profile is created.
    ''',
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=UserDetailSerializer,
            description='User registered successfully',
            examples=[
                OpenApiExample(
                    'Successful Registration',
                    value={
                        "success": True,
                        "message": "User registered successfully",
                        "data": {
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "farmer@example.com",
                                "username": "farmer1",
                                "first_name": "John",
                                "last_name": "Doe",
                                "role": "farmer",
                                "is_verified": False
                            },
                            "tokens": {
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                            }
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(description='Registration failed - validation errors')
    },
    examples=[
        OpenApiExample(
            'Farmer Registration',
            value={
                "email": "farmer@example.com",
                "username": "farmer1",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+254712345678",
                "role": "farmer"
            }
        )
    ]
)
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create appropriate profile based on role
            if user.role == 'farmer':
                FarmerProfile.objects.create(user=user, farm_size=0)
            elif user.role == 'buyer':
                BuyerProfile.objects.create(user=user)
            elif user.role == 'transporter':
                TransporterProfile.objects.create(
                    user=user,
                    vehicle_type='pickup',
                    vehicle_registration='',
                    vehicle_capacity=0,
                    license_number=''
                )

            # Create user profile
            UserProfile.objects.create(user=user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response(APIResponse.success({
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, "User registered successfully"), status=status.HTTP_201_CREATED)

        return Response(APIResponse.error(
            "Registration failed",
            serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['Authentication'],
    summary='User login',
    description='''
    Authenticate user and receive JWT tokens for API access.

    Returns both access and refresh tokens:
    - Access token: Short-lived (1 hour) for API requests
    - Refresh token: Long-lived (7 days) for getting new access tokens

    Include access token in Authorization header: `Bearer <access_token>`
    ''',
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            response=UserDetailSerializer,
            description='Login successful',
            examples=[
                OpenApiExample(
                    'Successful Login',
                    value={
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "farmer@example.com",
                                "username": "farmer1",
                                "role": "farmer",
                                "is_verified": True
                            },
                            "tokens": {
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                            }
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(description='Login failed - invalid credentials')
    },
    examples=[
        OpenApiExample(
            'Login Request',
            value={
                "email": "farmer@example.com",
                "password": "SecurePass123!"
            }
        )
    ]
)
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response(APIResponse.success({
                'user': UserDetailSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, "Login successful"), status=status.HTTP_200_OK)

        return Response(APIResponse.error(
            "Login failed",
            serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(APIResponse.success(
                UserDetailSerializer(user).data,
                "Profile updated successfully"
            ))

        return Response(APIResponse.error(
            "Profile update failed",
            serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class FarmerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.role != 'farmer':
            raise permissions.PermissionDenied("Only farmers can access this profile")
        profile, created = FarmerProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'farm_size': 0}
        )
        return profile

class BuyerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.role != 'buyer':
            raise permissions.PermissionDenied("Only buyers can access this profile")
        profile, created = BuyerProfile.objects.get_or_create(user=self.request.user)
        return profile

class TransporterProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TransporterProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.role != 'transporter':
            raise permissions.PermissionDenied("Only transporters can access this profile")
        profile, created = TransporterProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'vehicle_type': 'pickup',
                'vehicle_registration': '',
                'vehicle_capacity': 0,
                'license_number': ''
            }
        )
        return profile

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(APIResponse.success(
                message="Password changed successfully"
            ))

        return Response(APIResponse.error(
            "Password change failed",
            serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_phone_verification(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response(APIResponse.error("Phone number is required"),
                       status=status.HTTP_400_BAD_REQUEST)

    # Generate verification code
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = timezone.now() + timedelta(minutes=15)

    verification, created = PhoneVerification.objects.get_or_create(
        user=request.user,
        phone_number=phone_number,
        defaults={
            'verification_code': code,
            'expires_at': expires_at
        }
    )

    if not created:
        verification.verification_code = code
        verification.expires_at = expires_at
        verification.is_verified = False
        verification.save()

    # TODO: Send SMS using Africa's Talking API
    # For now, we'll return the code for testing
    return Response(APIResponse.success({
        'verification_code': code  # Remove this in production
    }, "Verification code sent"))

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone(request):
    serializer = PhoneVerificationConfirmSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['verification_code']

        try:
            verification = PhoneVerification.objects.get(
                user=request.user,
                phone_number=phone_number,
                verification_code=code,
                is_verified=False,
                expires_at__gt=timezone.now()
            )

            verification.is_verified = True
            verification.save()

            # Update user's phone verification status
            request.user.is_phone_verified = True
            request.user.phone_number = phone_number
            request.user.save()

            return Response(APIResponse.success(
                message="Phone number verified successfully"
            ))

        except PhoneVerification.DoesNotExist:
            return Response(APIResponse.error(
                "Invalid or expired verification code"
            ), status=status.HTTP_400_BAD_REQUEST)

    return Response(APIResponse.error(
        "Verification failed",
        serializer.errors
    ), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_email_verification(request):
    email = request.data.get('email', request.user.email)

    # Generate verification token
    token = generate_random_string(50)
    expires_at = timezone.now() + timedelta(hours=24)

    verification, created = EmailVerification.objects.get_or_create(
        user=request.user,
        email=email,
        defaults={
            'verification_token': token,
            'expires_at': expires_at
        }
    )

    if not created:
        verification.verification_token = token
        verification.expires_at = expires_at
        verification.is_verified = False
        verification.save()

    # Send verification email
    verification_url = f"https://agriconnect.co.ke/verify-email/?token={token}"
    message = f"Click the following link to verify your email: {verification_url}"

    if send_notification_email(email, "Verify your email - AgriConnect", message):
        return Response(APIResponse.success(
            message="Verification email sent"
        ))
    else:
        return Response(APIResponse.error(
            "Failed to send verification email"
        ), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    token = request.data.get('token')
    if not token:
        return Response(APIResponse.error("Verification token is required"),
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        verification = EmailVerification.objects.get(
            verification_token=token,
            is_verified=False,
            expires_at__gt=timezone.now()
        )

        verification.is_verified = True
        verification.save()

        # Update user's email verification status
        user = verification.user
        user.is_email_verified = True
        if verification.email != user.email:
            user.email = verification.email
        user.save()

        return Response(APIResponse.success(
            message="Email verified successfully"
        ))

    except EmailVerification.DoesNotExist:
        return Response(APIResponse.error(
            "Invalid or expired verification token"
        ), status=status.HTTP_400_BAD_REQUEST)
