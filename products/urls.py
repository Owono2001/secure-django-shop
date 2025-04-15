from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import product_list

urlpatterns = [
    # General Views
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('merchant/dashboard/', views.merchant_dashboard, name='merchant_dashboard'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Checkout
    path('checkout/', login_required(views.checkout), name='checkout'),

    # Product Management
    path('add_product/', login_required(views.add_product), name='add_product'),
    path('<int:pk>/edit/', login_required(views.edit_product), name='edit_product'),
    path('<int:pk>/delete/', login_required(views.delete_product), name='delete_product'),

    # Cart Management
    path('cart/add/<int:product_id>/', login_required(views.cart_add), name='cart_add'),
    path('cart/remove/<int:product_id>/', login_required(views.cart_remove), name='cart_remove'),
    path('cart/', login_required(views.cart_detail), name='cart_detail'),

    # Order History
    path('order-history/', login_required(views.order_history), name='order_history'),

    # Product Review
    path('product/<int:pk>/review/', login_required(views.product_review_view), name='product_review'),

    # Admin Order Management
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/orders/<int:order_id>/view/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/edit/<int:order_id>/', views.admin_order_edit, name='admin_order_edit'),
    path('admin/orders/delete/<int:order_id>/', views.admin_order_delete, name='admin_order_delete'),
    path('admin/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    
    # Merchant Order Management
    path('merchant/orders/', login_required(views.merchant_orders), name='merchant_orders'),
    path('merchant/products/', login_required(views.merchant_products), name='merchant_products'),
    path('merchant/orders/', login_required(views.merchant_order_list), name='merchant_order_list'),
    path('merchant/orders/<int:order_id>/', login_required(views.merchant_order_detail), name='merchant_order_detail'),  # Order detail
    path('<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('merchant/edit-product/<int:pk>/', views.edit_product, name='edit_product'),  # Edit product
    path('merchant/add-product/', views.add_product, name='add_product'),  # Add product
    path('merchant/delete-product/<int:pk>/', login_required(views.delete_product), name='merchant_delete_product'),
    path('merchant/orders/', views.merchant_order_list, name='merchant_order_list'),
    


    path('products/search/', views.product_search, name='search_results'),
    
    path('search/', views.product_list, name='search_results'),
]
