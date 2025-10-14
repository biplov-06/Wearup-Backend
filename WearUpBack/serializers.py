from rest_framework import serializers
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    Product, Size, Category, Color, ProductImage, ProductVariant, UserProfile, Address,
    Cart, CartItem, Order, OrderItem, ProductLike, ProductComment, ProductShare
)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main']


class ProductSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    main_image = serializers.ImageField(required=False, write_only=True)
    additional_images = serializers.ListField(child=serializers.ImageField(), required=False, allow_empty=True, write_only=True)
    images = serializers.SerializerMethodField()
    base_price_input = serializers.DecimalField(source='base_price', max_digits=10, decimal_places=2, write_only=True, required=False)
    seller = serializers.SerializerMethodField()
    name = serializers.CharField(source='product_name', read_only=True)
    price = serializers.DecimalField(source='final_price', max_digits=10, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    rating = serializers.DecimalField(source='average_rating', max_digits=3, decimal_places=1, read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    def get_sizes(self, obj):
        variants = obj.variants.all()
        return list(set([v.size.name for v in variants if v.size]))

    def get_categories(self, obj):
        return [category.name for category in obj.categories.all()]

    def get_images(self, obj):
        return ProductImageSerializer(obj.images.all(), many=True).data

    def get_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None

    def get_category(self, obj):
        first_category = obj.categories.first()
        return first_category.name if first_category else None

    def get_likes(self, obj):
        return obj.liked_by.count()

    def get_comments(self, obj):
        return obj.comments.count()

    def get_shares(self, obj):
        return obj.shared_by.count()

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(user=request.user).exists()
        return False

    def get_seller(self, obj):
        if obj.seller:
            try:
                profile = obj.seller.profile
                avatar = profile.profile_image.url if profile.profile_image else f'https://ui-avatars.com/api/?name={obj.seller.username}&size=40&background=667eea&color=fff'
                name = obj.seller.get_full_name() or obj.seller.username
                handle = f'@{obj.seller.username}'
                verified = profile.role in ['seller', 'admin']
                return {
                    'id': obj.seller.id,
                    'avatar': avatar,
                    'name': name,
                    'handle': handle,
                    'verified': verified
                }
            except UserProfile.DoesNotExist:
                return {
                    'id': obj.seller.id,
                    'avatar': f'https://ui-avatars.com/api/?name={obj.seller.username}&size=40&background=667eea&color=fff',
                    'name': obj.seller.username,
                    'handle': f'@{obj.seller.username}',
                    'verified': False
                }
        return None

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'description', 'gender', 'stock_quantity', 'sizes', 'categories', 'tags', 'base_price', 'discount_percentage', 'final_price', 'sku', 'status', 'is_featured', 'views', 'average_rating', 'main_image', 'additional_images', 'images', 'base_price_input', 'price', 'seller', 'name', 'image', 'category', 'rating', 'likes', 'comments', 'shares', 'user_liked']

    def create(self, validated_data):
        main_image = validated_data.pop('main_image', None)
        additional_images = validated_data.pop('additional_images', [])

        sizes_data = json.loads(self.initial_data.get('sizes', '[]'))
        categories_data = json.loads(self.initial_data.get('categories', '[]'))

        product = Product.objects.create(**validated_data)

        for size_name in sizes_data:
            size, created = Size.objects.get_or_create(name=size_name)
            product.sizes.add(size)

        for category_name in categories_data:
            category, created = Category.objects.get_or_create(name=category_name)
            product.categories.add(category)

        if main_image:
            ProductImage.objects.create(product=product, image=main_image, is_main=True)

        for img in additional_images:
            ProductImage.objects.create(product=product, image=img, is_main=False)

        return product

    def update(self, instance, validated_data):
        # Only update sizes/categories if provided in the request
        if 'sizes' in self.initial_data and self.initial_data['sizes']:
            try:
                sizes_data = json.loads(self.initial_data['sizes'])
                if isinstance(sizes_data, list):
                    instance.sizes.clear()
                    for size_name in sizes_data:
                        if size_name:  # Skip empty strings
                            size, created = Size.objects.get_or_create(name=size_name)
                            instance.sizes.add(size)
            except (json.JSONDecodeError, ValueError):
                # Log error if needed, but continue without updating sizes
                pass
        
        if 'categories' in self.initial_data and self.initial_data['categories']:
            try:
                categories_data = json.loads(self.initial_data['categories'])
                if isinstance(categories_data, list):
                    instance.categories.clear()
                    for category_name in categories_data:
                        if category_name:  # Skip empty strings
                            category, created = Category.objects.get_or_create(name=category_name)
                            instance.categories.add(category)
            except (json.JSONDecodeError, ValueError):
                # Log error if needed, but continue without updating categories
                pass

        main_image = validated_data.pop('main_image', None)
        additional_images = validated_data.pop('additional_images', [])

        instance = super().update(instance, validated_data)

        # Only update images if new ones are provided
        if main_image is not None or additional_images:
            try:
                # Delete only if updating images
                if main_image is not None or additional_images:
                    # Set existing main image to non-main if new main provided
                    if main_image:
                        instance.images.filter(is_main=True).update(is_main=False)
                    instance.images.all().delete()  # Still delete to recreate, but only if changing
                    if main_image:
                        ProductImage.objects.create(product=instance, image=main_image, is_main=True)
                    for img in additional_images:
                        ProductImage.objects.create(product=instance, image=img, is_main=False)
            except Exception as e:
                # Log the error, but don't fail the entire update
                print(f"Image update error: {e}")
                pass

        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include email and password.')
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'bio', 'location', 'website', 'business_name', 'profile_image', 'cover_image', 'phone', 'alternate_email', 'date_of_birth', 'gender']


# class WishlistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Wishlist
#         fields = '__all__'


# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = '__all__'


class ProductLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLike
        fields = '__all__'


class ProductCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        if obj.replies.exists():
            return ProductCommentSerializer(obj.replies.all(), many=True).data
        return []

    class Meta:
        model = ProductComment
        fields = ['id', 'user', 'product', 'content', 'parent', 'replies', 'created_at', 'updated_at']


class ProductShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductShare
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        return CartItemSerializer(obj.items.all(), many=True).data

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('cart',)


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.order_items.all(), many=True).data

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'payment_status', 'total_amount', 'created_at', 'order_items']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
