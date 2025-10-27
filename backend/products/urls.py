from django.urls import path
from . import views

urlpatterns = [
    # Product Categories
    path('categories/', views.ProductCategoryListView.as_view(), name='product-categories'),

    # Product CRUD
    path('', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('my-products/', views.MyProductsListView.as_view(), name='my-products'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<uuid:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<uuid:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    # Product Reviews
    path('<uuid:product_id>/reviews/', views.ProductReviewCreateView.as_view(), name='product-review-create'),

    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('<uuid:product_id>/wishlist/add/', views.add_to_wishlist, name='add-to-wishlist'),
    path('<uuid:product_id>/wishlist/remove/', views.remove_from_wishlist, name='remove-from-wishlist'),

    # Analytics
    path('<uuid:product_id>/analytics/', views.product_analytics, name='product-analytics'),

    # Utility endpoints
    path('featured/', views.featured_products, name='featured-products'),
    path('search/suggestions/', views.search_suggestions, name='search-suggestions'),
]