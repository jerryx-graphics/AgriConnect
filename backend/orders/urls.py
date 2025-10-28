from django.urls import path
from . import views

urlpatterns = [
    # Cart Management
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/items/<uuid:item_id>/update/', views.update_cart_item, name='update-cart-item'),
    path('cart/items/<uuid:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),

    # Order Management
    path('', views.OrderListView.as_view(), name='order-list'),
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:order_id>/status/', views.update_order_status, name='update-order-status'),
    path('<uuid:order_id>/cancel/', views.cancel_order, name='cancel-order'),
    path('<uuid:order_id>/rate/', views.rate_order, name='rate-order'),

    # Delivery Management
    path('delivery-requests/', views.DeliveryRequestListView.as_view(), name='delivery-requests'),
    path('delivery-requests/<uuid:delivery_id>/accept/', views.accept_delivery_request, name='accept-delivery'),
]