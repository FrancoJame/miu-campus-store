from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Product, Category, Cart, CartItem, Order, OrderItem
from django.db.models import Sum, Count
from .forms import SignupForm, ProductForm, CheckoutForm

def is_manager(user):
    return user.is_authenticated and user.role == User.Role.MANAGER

def is_staff(user):
    return user.is_authenticated and (user.role == User.Role.STAFF or user.role == User.Role.MANAGER)

def access_denied(request):
    return render(request, 'core/access_denied.html')

def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'core/home.html', {'products': products})

def product_list(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q')
    products = Product.objects.filter(is_active=True)
    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(name__icontains=query)
    categories = Category.objects.all()
    return render(request, 'core/product_list.html', {'products': products, 'categories': categories})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to MIU Store.")
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == User.Role.MANAGER:
        return manager_dashboard(request)
    elif request.user.role == User.Role.STAFF:
        return staff_dashboard(request)
    else:
        return customer_dashboard(request)

@user_passes_test(is_manager)
def manager_dashboard(request):
    total_products = Product.objects.count()
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    total_revenue = Order.objects.filter(status=Order.Status.DELIVERED).aggregate(Sum('total_price'))['total_price__sum'] or 0
    top_products = Product.objects.annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold')[:5]
    
    context = {
        'total_products': total_products,
        'orders_by_status': orders_by_status,
        'total_revenue': total_revenue,
        'top_products': top_products,
    }
    return render(request, 'core/dashboards/manager.html', context)

@user_passes_test(is_staff)
def staff_dashboard(request):
    pending_orders = Order.objects.filter(status=Order.Status.PENDING).count()
    low_stock_products = Product.objects.filter(stock_quantity__lt=5)
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    context = {
        'pending_orders_count': pending_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'core/dashboards/staff.html', context)

@login_required
def customer_dashboard(request):
    active_orders = Order.objects.filter(user=request.user).exclude(status__in=[Order.Status.DELIVERED, Order.Status.CANCELLED])
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'active_orders': active_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'core/dashboards/customer.html', context)

@user_passes_test(is_staff)
def manage_orders(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'core/staff/order_list.html', {'orders': orders, 'statuses': Order.Status.choices})

@user_passes_test(is_staff)
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in Order.Status.values:
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.reference_number} updated to {new_status}")
        return redirect('manage_orders')
    return render(request, 'core/staff/order_detail.html', {'order': order})

@user_passes_test(is_manager)
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        if order.status != Order.Status.CANCELLED:
            # Reversal of stock
            for item in order.items.all():
                if item.product:
                    item.product.stock_quantity += item.quantity
                    item.product.save()
            order.status = Order.Status.CANCELLED
            order.save()
            messages.success(request, f"Order {order.reference_number} cancelled and stock reversed.")
        return redirect('manage_orders')
    return render(request, 'core/staff/order_detail.html', {'order': order})

@user_passes_test(is_manager)
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'core/manager/product_list.html', {'products': products})

@user_passes_test(is_manager)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully!")
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'core/manager/product_form.html', {'form': form, 'title': 'Create Product'})

@user_passes_test(is_manager)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/manager/product_form.html', {'form': form, 'title': 'Update Product'})

@user_passes_test(is_manager)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False # Soft delete
        product.save()
        messages.success(request, "Product deactivated successfully!")
        return redirect('manage_products')
    return render(request, 'core/manager/product_confirm_delete.html', {'product': product})

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.line_total for item in items)
    return render(request, 'core/cart.html', {'items': items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock_quantity <= 0:
        messages.error(request, "Sorry, this product is out of stock.")
        return redirect('product_list')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_detail')

@login_required
def update_cart_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if action == 'increase':
        if cart_item.product.stock_quantity > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f"Only {cart_item.product.stock_quantity} items available in stock.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
            
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = getattr(request.user, 'cart', None)
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('product_list')
    
    items = cart.items.all()
    total = sum(item.line_total for item in items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Check stock one last time
            for item in items:
                if item.product.stock_quantity < item.quantity:
                    messages.error(request, f"Insufficient stock for {item.product.name}.")
                    return redirect('cart_detail')
            
            # Create Order
            order = Order.objects.create(
                user=request.user,
                total_price=total,
                delivery_address=form.cleaned_data['delivery_address']
            )
            
            # Create Order Items and Reduce Stock
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_order=item.product.price
                )
                item.product.stock_quantity -= item.quantity
                item.product.save()
            
            # Clear Cart
            cart.items.all().delete()
            
            messages.success(request, f"Order placed successfully! Reference: {order.reference_number}")
            return redirect('dashboard')
    else:
        form = CheckoutForm(initial={'delivery_address': request.user.address})
    
    return render(request, 'core/checkout.html', {'form': form, 'items': items, 'total': total})
