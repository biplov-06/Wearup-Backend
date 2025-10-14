
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Product, UserProfile, Cart, CartItem, Order, OrderItem, ProductLike, ProductComment, ProductShare
from .serializers import ProductSerializer, RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, ProductLikeSerializer, ProductCommentSerializer, ProductShareSerializer


# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


# class SizeViewSet(viewsets.ModelViewSet):
#     queryset = Size.objects.all()
#     serializer_class = SizeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'list':
            queryset = Product.objects.all()
            seller_id = self.request.query_params.get('seller')
            user_id = self.request.query_params.get('user')
            search_query = self.request.query_params.get('search')

            if seller_id:
                queryset = queryset.filter(seller_id=seller_id)
            elif user_id:
                queryset = queryset.filter(seller_id=user_id)

            if search_query:
                queryset = queryset.filter(
                    product_name__icontains=search_query
                ) | queryset.filter(
                    description__icontains=search_query
                ) | queryset.filter(
                    categories__icontains=search_query
                )

            return queryset
        elif self.request.user.is_authenticated:
            return Product.objects.filter(seller=self.request.user)
        return Product.objects.none()

    def get_permissions(self):
        # Allow public read access, but require authentication for create/update/delete
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Only set seller when the request user is an authenticated User instance.
        # Passing AnonymousUser into model fields causes a ValueError when assigning
        # a related User field during Product creation.
        seller = None
        try:
            if hasattr(self.request, 'user') and self.request.user.is_authenticated:
                seller = self.request.user
        except Exception:
            seller = None

        serializer.save(seller=seller)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if product has been ordered
        if OrderItem.objects.filter(product=instance).exists():
            return Response(
                {'error': 'Cannot delete product that has been ordered'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            print(f"Error deleting product: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductLikeViewSet(viewsets.ModelViewSet):
    queryset = ProductLike.objects.all()
    serializer_class = ProductLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductLike.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductCommentViewSet(viewsets.ModelViewSet):
    queryset = ProductComment.objects.all()
    serializer_class = ProductCommentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return ProductComment.objects.filter(product_id=product_id)
        return ProductComment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductShareViewSet(viewsets.ModelViewSet):
    queryset = ProductShare.objects.all()
    serializer_class = ProductShareSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductShare.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart, product_id=self.request.data.get('product'))


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Handle user fields update
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data['first_name']
        if 'last_name' in request.data:
            user_data['last_name'] = request.data['last_name']
        if user_data:
            for key, value in user_data.items():
                setattr(request.user, key, value)
            request.user.save()

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # Add detailed error logging for debugging
            print("UserProfile update errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_user_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_product_like(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    like, created = ProductLike.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        like.delete()
        return Response({'liked': False, 'likes_count': product.liked_by.count()})

    return Response({'liked': True, 'likes_count': product.liked_by.count()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    platform = request.data.get('platform', 'copy_link')

    share = ProductShare.objects.create(
        user=request.user,
        product=product,
        platform=platform
    )

    return Response({
        'shared': True,
        'platform': platform,
        'shares_count': product.shared_by.count()
    })
