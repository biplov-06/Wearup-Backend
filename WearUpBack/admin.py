from django.contrib import admin
from .models import (
    Product, Category, Size, Color, ProductImage, ProductVariant, UserProfile, Address,
    Cart, CartItem, Order, OrderItem, Coupon, ProductView
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'seller', 'base_price', 'final_price', 'stock_quantity', 'status', 'is_featured']
    list_filter = ['gender', 'status', 'is_featured', 'categories']
    search_fields = ['product_name', 'description', 'seller__username', 'sku']
    filter_horizontal = ['categories']
    readonly_fields = ['final_price', 'average_rating', 'views']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']
    search_fields = ['name']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_main', 'order']
    list_filter = ['is_main']
    ordering = ['order']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock_quantity', 'price_adjustment']
    list_filter = ['size', 'color']
    search_fields = ['product__product_name', 'sku']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'location', 'business_name']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email', 'business_name']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'full_name', 'city', 'country', 'is_default']
    list_filter = ['address_type', 'country', 'is_default']
    search_fields = ['user__username', 'full_name', 'city']


# # @admin.register(Wishlist)
# # class WishlistAdmin(admin.ModelAdmin):
# #     list_display = ['user', 'product', 'added_at']
# #     list_filter = ['added_at']
# #     search_fields = ['user__username', 'product__product_name']


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'rating', 'is_verified_purchase', 'created_at']
#     list_filter = ['rating', 'is_verified_purchase', 'created_at']
#     search_fields = ['user__username', 'product__product_name', 'comment']


# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'content', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['user__username', 'product__product_name', 'content']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'added_at']
    list_filter = ['quantity', 'added_at']
    search_fields = ['cart__user__username', 'product__product_name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_number', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__username', 'order_number']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'unit_price', 'total_price']
    list_filter = ['quantity']
    search_fields = ['order__user__username', 'product__product_name']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'viewed_at', 'session_id']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'product__product_name', 'session_id']
