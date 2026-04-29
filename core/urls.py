from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views, api_views, forms

router = DefaultRouter()
router.register(r'products', api_views.ProductViewSet)
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'orders', api_views.OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    # path('products/<int:pk>/', views.product_detail, name='product_detail'), # To be implemented
    
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        authentication_form=forms.LoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.customer_dashboard, name='profile'),
    path('access-denied/', views.access_denied, name='access_denied'),
    
    # Manager Product Management
    path('manager/products/', views.manage_products, name='manage_products'),
    path('manager/products/create/', views.product_create, name='product_create'),
    path('manager/products/update/<int:pk>/', views.product_update, name='product_update'),
    path('manager/products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    
    # Staff/Manager Order Management
    path('staff/orders/', views.manage_orders, name='manage_orders'),
    path('staff/orders/<int:pk>/status/', views.order_update_status, name='order_update_status'),
    path('manager/orders/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    
    # Cart and Checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
]
