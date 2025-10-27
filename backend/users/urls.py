from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User Profile Management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/details/', views.UserProfileDetailView.as_view(), name='user-profile-details'),
    path('profile/farmer/', views.FarmerProfileView.as_view(), name='farmer-profile'),
    path('profile/buyer/', views.BuyerProfileView.as_view(), name='buyer-profile'),
    path('profile/transporter/', views.TransporterProfileView.as_view(), name='transporter-profile'),

    # Password Management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),

    # Phone Verification
    path('phone/send-verification/', views.send_phone_verification, name='send-phone-verification'),
    path('phone/verify/', views.verify_phone, name='verify-phone'),

    # Email Verification
    path('email/send-verification/', views.send_email_verification, name='send-email-verification'),
    path('email/verify/', views.verify_email, name='verify-email'),
]