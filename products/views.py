import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Product, Order, OrderItem, Category, Review
from .forms import ProductForm, CheckoutForm, ProductReviewForm, OrderForm
from .cart import Cart
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db import transaction
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from oauth2_provider.decorators import protected_resource
from .serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from haystack import indexes

# Setup logger
logger = logging.getLogger(__name__)

# Role-based access control (RBAC) for merchants
def is_merchant(user):
    return user.role == 'merchant'

def is_admin(user):
    return user.role == 'admin'

def is_customer(user):
    return user.role == 'customer'

# --- Dashboard Views Based on Role ---
#@login_required
#@user_passes_test(is_admin)
#def admin_dashboard(request):
    #logger.info("Admin dashboard accessed")
    #return render(request, 'admin_dashboard.html')
    #return render(request, 'users/admin_dashboard.html')

@login_required
@user_passes_test(is_merchant)
def merchant_products(request):
    logger.info(f"Merchant {request.user.username} accessed products")
    products = Product.objects.filter(merchant=request.user)
    return render(request, 'merchant_products.html', {'products': products})

# Merchant Orders Management View
@login_required
@user_passes_test(is_merchant)
def merchant_orders(request):
    logger.info(f"Merchant {request.user.username} accessed their orders")
    orders = Order.objects.filter(orderitem__product__merchant=request.user).distinct()
    return render(request, 'products/merchant_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_customer)
def order_history(request):
    logger.info(f"Customer {request.user.username} accessed their order history")
    orders = request.user.order_set.all()
    return render(request, 'products/order_history.html', {'orders': orders})

# --- General Dashboard View (Used for All Users) ---
@login_required
def dashboard(request):
    logger.info(f"Dashboard accessed by {request.user.username}")
    return render(request, 'users/dashboard.html')


@login_required
@transaction.atomic
def checkout(request):
    cart = Cart(request)
    logger.info(f"Checkout started for {request.user.username}")

    # Clear any stale duplicate submission flag on GET requests.
    if request.method == "GET" and request.session.get('order_in_progress'):
        logger.debug("Clearing stale order_in_progress flag on GET request")
        del request.session['order_in_progress']

    if len(cart) == 0:
        logger.warning("Attempted checkout with an empty cart")
        messages.error(request, "Your cart is empty.")
        return redirect('product_list')

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            logger.warning(f"Invalid checkout form submitted by {request.user.username}: {form.errors}")
            messages.error(request, "Please correct the errors in the form and try again.")
            return render(request, 'products/checkout.html', {'cart': cart, 'form': form})

        try:
            # Prevent duplicate submissions.
            if request.session.get('order_in_progress', False):
                logger.warning(f"Duplicate checkout attempt by {request.user.username}")
                messages.error(request, "You already placed this order.")
                return redirect('customer_dashboard')

            # Create and save the order.
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(item['price'] * item['quantity'] for item in cart)
            order.is_paid = False  # Mark as unpaid initially.
            order.save()
            logger.debug(f"Order created with ID: {order.id}")

            # Create order items and update product stock.
            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if quantity > product.stock:
                    logger.error(f"Insufficient stock for {product.name}: requested {quantity}, available {product.stock}")
                    raise ValueError(f"Not enough stock for {product.name}.")

                # Deduct stock.
                product.stock -= quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item['price'],
                    quantity=quantity
                )

            # Set a session flag to block duplicate submissions.
            request.session['order_in_progress'] = True

            # Clear the cart after successful checkout.
            cart.clear()
            logger.info(f"Checkout completed successfully for {request.user.username}, order ID: {order.id}")
            messages.success(request, "Your order has been placed successfully.")

            # Clear the duplicate submission flag so future orders are allowed.
            if 'order_in_progress' in request.session:
                del request.session['order_in_progress']

            return redirect('customer_dashboard')

        except ValueError as e:
            logger.error(f"Error during checkout for {request.user.username}: {e}")
            messages.error(request, str(e))
            return redirect('cart_detail')

        except Exception as e:
            logger.error(f"Unexpected error during checkout for {request.user.username}: {e}")
            messages.error(request, "There was an unexpected error during checkout. Please try again.")
            return render(request, 'products/checkout.html', {'cart': cart, 'form': form})
    else:
        form = CheckoutForm()

    return render(request, 'products/checkout.html', {'cart': cart, 'form': form})

# --- Product Views (Accessible by All Users) ---
def product_list(request):
    logger.info("Product list accessed")
    category_name = request.GET.get('category', '')  # Get category filter from the URL
    search_query = request.GET.get('q', '')  # Get search query from the URL

    # Filter products based on category or search query
    if category_name:
        products = Product.objects.filter(category__name__icontains=category_name).select_related('category')
    elif search_query:
        products = Product.objects.filter(name__icontains=search_query).select_related('category')
    else:
        products = Product.objects.all().select_related('category')

    # Add explicit ordering
    products = products.order_by('-created_at')  # Order by the most recently created products

    # Pagination setup (6 products per page)
    paginator = Paginator(products, 6)  # Adjust the number of products per page as needed
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)

    # Retrieve all categories for the category filter dropdown
    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {
        'products': page_obj,  # Paginated products for the current page
        'categories': categories,  # List of all categories for the dropdown
        'category_name': category_name,  # Current category filter
        'search_query': search_query,  # Current search query
    })


# --- Homepage View ---
def homepage(request):
    logger.info("Homepage accessed")
    categories = Product.objects.values('category').distinct()
    featured_products = Product.objects.order_by('-created_at')[:6]  # Latest 6 products
    return render(request, 'products/homepage.html', {
        'categories': categories,
        'featured_products': featured_products
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    logger.info(f"Product detail accessed for product ID {pk}")
    reviews = product.reviews.all()  # Fetch all reviews for the product
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })

# Role check for merchants
def is_merchant(user):
    return user.role == 'merchant'

@login_required
@user_passes_test(lambda u: u.role == 'merchant')  # Restrict access to merchants
def merchant_dashboard(request):
    """
    Display the Merchant Dashboard with products added by the merchant.
    """
    logger.info(f"Merchant {request.user.username} accessed the Merchant Dashboard.")
    products = Product.objects.filter(merchant=request.user).order_by('-created_at')  # Fetch products added by this merchant
    logger.debug(f"Products fetched for {request.user.username}: {products}")
    return render(request, 'users/merchant_dashboard.html', {'products': products})

# --- Add, Edit, Delete Products (Restricted to Merchants) ---
@login_required
@user_passes_test(lambda u: u.role == 'merchant')  # Restrict access to merchants
def add_product(request):
    """
    View for merchants to add a new product to their store.
    """
    logger.info(f"Merchant {request.user.username} accessed the Add Product page.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data['name']
            category = form.cleaned_data['category']

            # Validation: Check if the product already exists in the same category
            if Product.objects.filter(name__iexact=product_name, category=category, merchant=request.user).exists():
                logger.warning(
                    f"Merchant {request.user.username} attempted to add a duplicate product: '{product_name}' in category '{category}'."
                )
                messages.error(
                    request,
                    f'Product "{product_name}" already exists in the "{category}" category under your store.'
                )
                return redirect('add_product')  # Redirect back to the form
            
            # Save the product and assign the logged-in merchant
            product = form.save(commit=False)
            product.merchant = request.user
            product.save()
            logger.info(f"Merchant {request.user.username} successfully added a new product: '{product_name}' in category '{category}'.")
            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('merchant_dashboard')  # Redirect to the merchant dashboard after adding the product
        else:
            logger.warning(f"Invalid form submission by Merchant {request.user.username}. Errors: {form.errors}")

    else:
        logger.info(f"Merchant {request.user.username} accessed the Add Product form.")
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'merchant')  # Restrict access to merchants
def edit_product(request, pk):
    """
    Edit a product owned by the merchant.
    """
    product = get_object_or_404(Product, pk=pk, merchant=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('merchant_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/add_product.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'merchant')  # Restrict access to merchants
def delete_product(request, pk):
    """
    Delete a product owned by the merchant.
    """
    product = get_object_or_404(Product, pk=pk, merchant=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('merchant_dashboard')
    return render(request, 'products/confirm_delete.html', {'product': product})

# --- Cart Management Views ---
def cart_detail(request):
    logger.info(f"Cart detail accessed by {request.user.username}")
    cart = Cart(request)
    return render(request, 'products/cart_detail.html', {'cart': cart})

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    logger.info(f"Product {product.name} removed from cart by {request.user.username}")
    messages.success(request, f"{product.name} removed from cart.")
    return redirect('cart_detail')

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    logger.info(f"Product {product.name} added to cart by {request.user.username}")
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_detail')

# --- Product Review View (Customers Can Leave Reviews) ---
@login_required
def product_review_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    logger.info(f"Accessing review page for product ID {pk} by user {request.user.username}")
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            if request.user.role not in ['customer']:
                messages.error(request, "Only customers can submit reviews.")
                return redirect('product_detail', pk=pk)

            # Save the review
            Review.objects.create(
                product=product,
                user=request.user,
                content=form.cleaned_data['review'],
                rating=5  # Assuming a default rating
            )
            messages.success(request, "Your review has been submitted!")
            return redirect('product_detail', pk=pk)
    else:
        form = ProductReviewForm()
    return render(request, 'products/product_review.html', {'form': form, 'product': product})

# --- Admin Order Management Views ---
@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    logger.info(f"Admin {request.user.username} accessed order list. Total orders: {orders.count()}")
    return render(request, 'products/admin_order_list.html', {'orders': orders})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    logger.info(f"Admin {request.user.username} accessed details for order ID {order_id}")

    # Calculate totals for each item
    order_items_with_total = []
    for item in order.orderitem_set.all():
        order_items_with_total.append({
            'product': item.product.name,
            'price': item.price,
            'quantity': item.quantity,
            'total': item.price * item.quantity
        })

    return render(request, 'products/admin_order_detail.html', {
        'order': order,
        'order_items': order_items_with_total
    })

@staff_member_required
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    logger.info(f"Admin {request.user.username} accessed edit page for order ID {order_id}")
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            logger.info(f"Order ID {order_id} updated successfully by admin {request.user.username}")
            messages.success(request, 'Order updated successfully.')
            return redirect('admin_order_list')
        else:
            logger.warning(f"Invalid order form submission for order ID {order_id} by admin {request.user.username}")
            messages.error(request, 'Error updating the order. Please check the form.')
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'products/admin_order_edit.html', {'form': form, 'order': order})

@staff_member_required
def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    logger.info(f"Admin {request.user.username} accessed delete page for order ID {order_id}")
    
    if request.method == 'POST':
        order.delete()
        logger.info(f"Order ID {order_id} deleted successfully by admin {request.user.username}")
        messages.success(request, 'Order deleted successfully.')
        return redirect('admin_order_list')
    
    return render(request, 'products/admin_order_confirm_delete.html', {'order': order})


@protected_resource
def secure_api_view(request):
    # Secure API logic
    logger.info(f"Secure API accessed by user {request.user.username}")
    data = {
        'message': 'This is a protected API response.',
        'user': request.user.username,
    }
    return JsonResponse(data)

@api_view(['POST'])
def validate_product_view(request):
    logger.info("Product validation API called")
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        logger.info("Product validation successful")
        return Response({'message': 'Data is valid'}, status=status.HTTP_200_OK)
    logger.warning("Product validation failed")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@staff_member_required
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    logger.info(f"Admin {request.user.username} accessed view page for order ID {order_id}")
    order_items = order.items.all()  # Assuming related_name='items' in OrderItem model
    return render(request, 'admin/view_order.html', {'order': order, 'order_items': order_items})

def product_search(request):
    query = request.GET.get('q', '')  # Get the search query from the URL
    logger.info(f"Product search initiated with query: {query}")
    products = Product.objects.filter(name__icontains=query) if query else []

    # Check if the request is an AJAX request (for live search)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('products/partials/product_list.html', {'products': products})
        logger.info(f"AJAX product search results for query: {query}")
        return JsonResponse({'html': html})

    # Render full search results page for non-AJAX requests
    logger.info(f"Full product search results displayed for query: {query}")
    return render(request, 'products/search_results.html', {
        'query': query,
        'products': products,
    })

@login_required
def order_history(request):
    logger.info(f"Order history accessed by user {request.user.username}")
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'products/order_history.html', {'orders': orders})

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Product


@login_required
@user_passes_test(lambda u: u.is_staff)  # Only admins can access this
def admin_product_list(request):
    """
    View for admins to see the list of all products.
    """
    logger.info(f"Admin {request.user.username} accessed product list")
    products = Product.objects.all().order_by('-created_at')  # Adjust based on your Product model
    return render(request, 'products/admin_product_list.html', {'products': products})

@login_required
@user_passes_test(lambda u: u.is_staff)  # Only admins can access this
def update_order_status(request, order_id):
    """
    View for updating the status of an order.
    """
    order = get_object_or_404(Order, id=order_id)
    logger.info(f"Admin {request.user.username} accessed update status page for order ID {order_id}")
    
    if request.method == 'POST':
        # Update the order's status from the form data
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            logger.info(f"Order ID {order_id} status updated to {new_status} by admin {request.user.username}")
            return redirect('admin_order_list')  # Redirect to the admin order list after updating

    return render(request, 'products/update_order_status.html', {'order': order})


@login_required
@user_passes_test(lambda u: u.is_merchant)  # Restrict access to merchants
def merchant_order_list(request):
    """
    View for merchants to list their orders.
    """
    logger.info(f"Merchant {request.user.username} accessed their order list")
    orders = Order.objects.filter(orderitem__product__merchant=request.user).distinct().order_by('-created_at')
    return render(request, 'products/merchant_order_list.html', {'orders': orders})


@login_required
@user_passes_test(lambda u: u.is_merchant)  # Restrict access to merchants
def merchant_order_detail(request, order_id):
    """
    View for merchants to see details of a specific order.
    """
    order = get_object_or_404(Order, id=order_id, orderitem__product__merchant=request.user)
    return render(request, 'products/merchant_order_detail.html', {'order': order})


