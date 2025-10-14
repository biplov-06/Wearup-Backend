"""
URL configuration for Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from WearUpBack.views import ProductViewSet, CartViewSet, CartItemViewSet, OrderViewSet, OrderItemViewSet, register_user, login_user, logout_user, user_profile, public_user_profile, ProductLikeViewSet, ProductCommentViewSet, ProductShareViewSet, toggle_product_like, share_product

router = DefaultRouter()
# router.register(r'categories', CategoryViewSet)
# router.register(r'sizes', SizeViewSet)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-likes', ProductLikeViewSet, basename='productlike')
router.register(r'product-comments', ProductCommentViewSet, basename='productcomment')
router.register(r'product-shares', ProductShareViewSet, basename='productshare')
# router.register(r'wishlists', WishlistViewSet, basename='wishlist')
# router.register(r'reviews', ReviewViewSet, basename='review')
# router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/login/', login_user, name='login'),
    path('api/auth/logout/', logout_user, name='logout'),
    path('api/auth/profile/', user_profile, name='profile'),
    path('api/users/<int:user_id>/', public_user_profile, name='public_user_profile'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/products/<int:product_id>/toggle-like/', toggle_product_like, name='toggle_product_like'),
    path('api/products/<int:product_id>/share/', share_product, name='share_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
