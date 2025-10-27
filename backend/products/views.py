from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Avg, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.utils import APIResponse, calculate_distance
from core.permissions import IsFarmerOrReadOnly
from .models import (
    ProductCategory, Product, ProductImage, ProductReview,
    Wishlist, ProductAnalytics
)
from .serializers import (
    ProductCategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductReviewCreateSerializer,
    WishlistSerializer, ProductAnalyticsSerializer
)

class ProductCategoryListView(generics.ListAPIView):
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=['Products'],
    summary='List all products',
    description='''
    Get a paginated list of all available products with advanced filtering and search capabilities.

    **Filtering Options:**
    - By location: county, sub_county
    - By product attributes: category, condition, quality_grade, is_organic
    - By price range: min_price, max_price
    - By distance: latitude, longitude, max_distance (in km)

    **Search:** Search in product name, description, tags, and farmer names

    **Ordering:** Sort by price_per_unit, created_at, quantity_available
    ''',
    parameters=[
        OpenApiParameter('category', OpenApiTypes.UUID, description='Filter by product category ID'),
        OpenApiParameter('county', OpenApiTypes.STR, description='Filter by county name'),
        OpenApiParameter('sub_county', OpenApiTypes.STR, description='Filter by sub-county name'),
        OpenApiParameter('condition', OpenApiTypes.STR, description='Product condition: fresh, good, fair, dried, processed'),
        OpenApiParameter('quality_grade', OpenApiTypes.STR, description='Quality grade: premium, standard, economic'),
        OpenApiParameter('is_organic', OpenApiTypes.BOOL, description='Filter organic products only'),
        OpenApiParameter('min_price', OpenApiTypes.DECIMAL, description='Minimum price per unit'),
        OpenApiParameter('max_price', OpenApiTypes.DECIMAL, description='Maximum price per unit'),
        OpenApiParameter('latitude', OpenApiTypes.DECIMAL, description='Your latitude for distance-based filtering'),
        OpenApiParameter('longitude', OpenApiTypes.DECIMAL, description='Your longitude for distance-based filtering'),
        OpenApiParameter('max_distance', OpenApiTypes.DECIMAL, description='Maximum distance in kilometers (default: 50km)'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in product names, descriptions, and farmer names'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: price_per_unit, -price_per_unit, created_at, -created_at'),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductListSerializer,
            description='List of products',
            examples=[
                OpenApiExample(
                    'Product List Response',
                    value={
                        "count": 25,
                        "next": "http://localhost:8000/api/v1/products/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "Fresh Bananas",
                                "description": "Sweet and ripe bananas from our organic farm",
                                "price_per_unit": "150.00",
                                "unit": "kg",
                                "quantity_available": "500.00",
                                "county": "Kisii",
                                "farmer_name": "John Doe",
                                "category_name": "Fruits",
                                "primary_image": "http://localhost:8000/media/products/bananas.jpg",
                                "average_rating": 4.5,
                                "review_count": 12
                            }
                        ]
                    }
                )
            ]
        )
    }
)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'county', 'sub_county', 'condition', 'quality_grade', 'is_organic']
    search_fields = ['name', 'description', 'tags', 'farmer__first_name', 'farmer__last_name']
    ordering_fields = ['price_per_unit', 'created_at', 'quantity_available']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True, is_deleted=False).select_related(
            'farmer', 'category'
        ).prefetch_related('images', 'reviews')

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_unit__lte=max_price)

        # Filter by location proximity
        user_lat = self.request.query_params.get('latitude')
        user_lon = self.request.query_params.get('longitude')
        max_distance = self.request.query_params.get('max_distance', 50)  # Default 50km

        if user_lat and user_lon:
            # This is a simplified distance filter - in production use PostGIS
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                max_distance = float(max_distance)

                # Filter products with location data
                products_with_location = queryset.filter(
                    latitude__isnull=False,
                    longitude__isnull=False
                )

                # Calculate distances and filter
                filtered_products = []
                for product in products_with_location:
                    distance = calculate_distance(
                        user_lat, user_lon,
                        float(product.latitude), float(product.longitude)
                    )
                    if distance <= max_distance:
                        filtered_products.append(product.id)

                queryset = queryset.filter(id__in=filtered_products)
            except (ValueError, TypeError):
                pass

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add distance calculation context if location provided
        user_lat = self.request.query_params.get('latitude')
        user_lon = self.request.query_params.get('longitude')
        if user_lat and user_lon:
            context['user_location'] = (float(user_lat), float(user_lon))
        return context

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_available=True, is_deleted=False)
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track product view
        analytics, created = ProductAnalytics.objects.get_or_create(product=instance)
        analytics.views_count += 1
        analytics.last_viewed = timezone.now()
        analytics.save()

        serializer = self.get_serializer(instance)
        return Response(APIResponse.success(serializer.data))

class MyProductsListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'condition', 'quality_grade', 'is_organic', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['price_per_unit', 'created_at', 'quantity_available']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(
            farmer=self.request.user,
            is_deleted=False
        ).select_related('category').prefetch_related('images', 'reviews')

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrReadOnly]

    def create(self, request, *args, **kwargs):
        if request.user.role != 'farmer':
            return Response(
                APIResponse.error("Only farmers can create products"),
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                APIResponse.success(
                    ProductDetailSerializer(product, context={'request': request}).data,
                    "Product created successfully"
                ),
                status=status.HTTP_201_CREATED
            )

        return Response(
            APIResponse.error("Product creation failed", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

class ProductUpdateView(generics.UpdateAPIView):
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(farmer=self.request.user, is_deleted=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            product = serializer.save()
            return Response(
                APIResponse.success(
                    ProductDetailSerializer(product, context={'request': request}).data,
                    "Product updated successfully"
                )
            )

        return Response(
            APIResponse.error("Product update failed", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(farmer=self.request.user, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

        return Response(
            APIResponse.success(message="Product deleted successfully"),
            status=status.HTTP_204_NO_CONTENT
        )

class ProductReviewCreateView(generics.CreateAPIView):
    serializer_class = ProductReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product'] = Product.objects.get(pk=self.kwargs['product_id'])
        return context

    def create(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=kwargs['product_id'])
        except Product.DoesNotExist:
            return Response(
                APIResponse.error("Product not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        if product.farmer == request.user:
            return Response(
                APIResponse.error("You cannot review your own product"),
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already reviewed this product
        if ProductReview.objects.filter(product=product, buyer=request.user).exists():
            return Response(
                APIResponse.error("You have already reviewed this product"),
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                APIResponse.success(
                    ProductReviewCreateSerializer(review).data,
                    "Review added successfully"
                ),
                status=status.HTTP_201_CREATED
            )

        return Response(
            APIResponse.error("Review creation failed", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

class WishlistView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).select_related('product__farmer', 'product__category')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(pk=product_id, is_available=True, is_deleted=False)
    except Product.DoesNotExist:
        return Response(
            APIResponse.error("Product not found"),
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        return Response(
            APIResponse.success(message="Product added to wishlist"),
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            APIResponse.error("Product already in wishlist"),
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_wishlist(request, product_id):
    try:
        wishlist_item = Wishlist.objects.get(
            user=request.user,
            product_id=product_id,
            is_deleted=False
        )
        wishlist_item.is_deleted = True
        wishlist_item.deleted_at = timezone.now()
        wishlist_item.save()

        return Response(
            APIResponse.success(message="Product removed from wishlist"),
            status=status.HTTP_204_NO_CONTENT
        )
    except Wishlist.DoesNotExist:
        return Response(
            APIResponse.error("Product not in wishlist"),
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_analytics(request, product_id):
    try:
        product = Product.objects.get(pk=product_id, farmer=request.user, is_deleted=False)
        analytics, created = ProductAnalytics.objects.get_or_create(product=product)

        serializer = ProductAnalyticsSerializer(analytics)
        return Response(APIResponse.success(serializer.data))

    except Product.DoesNotExist:
        return Response(
            APIResponse.error("Product not found"),
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products(request):
    products = Product.objects.filter(
        is_featured=True,
        is_available=True,
        is_deleted=False
    ).select_related('farmer', 'category').prefetch_related('images')[:10]

    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return Response(APIResponse.success(serializer.data))

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    query = request.query_params.get('q', '').strip()
    if len(query) < 2:
        return Response(APIResponse.success([]))

    # Get product name suggestions
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(tags__contains=[query]),
        is_available=True,
        is_deleted=False
    ).values_list('name', flat=True).distinct()[:5]

    # Get category suggestions
    categories = ProductCategory.objects.filter(
        name__icontains=query,
        is_active=True
    ).values_list('name', flat=True)[:3]

    suggestions = list(products) + list(categories)
    return Response(APIResponse.success(suggestions[:8]))
