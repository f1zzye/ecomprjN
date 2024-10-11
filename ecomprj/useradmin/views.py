from django.shortcuts import render, redirect
from core.models import CartOrder, Product, Category, CartOrderItems, ProductReview
from django.db.models import Sum
from userauths.models import User, Profile
from django.contrib import messages
from useradmin.forms import AddProductForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from useradmin.decorators import admin_required
from django.core.paginator import Paginator

import datetime

@admin_required
def dashboard(request):
    revenue = CartOrder.objects.aggregate(price=Sum('price'))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by('-id')
    latest_orders = CartOrder.objects.all()

    this_month = datetime.datetime.now().month

    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum('price'))

    context = {
        'revenue': revenue,
        'total_orders_count': total_orders_count,
        'all_products': all_products,
        'all_categories': all_categories,
        'new_customers': new_customers,
        'latest_orders': latest_orders,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, "useradmin/dashboard.html", context)


@admin_required
def products(request, page=1):
    all_products = Product.objects.all().order_by('-id')
    all_categories = Category.objects.all()

    per_page = 5
    paginator = Paginator(all_products, per_page)
    products_paginator = paginator.page(page)

    context = {
        'all_products': products_paginator,
        'all_categories': all_categories,
    }
    return render(request, "useradmin/products.html", context)


@admin_required
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect('useradmin:dashboard')
    else:
        form = AddProductForm()

    context = {
        'form': form,
    }

    return render(request, "useradmin/add-product.html", context)


@admin_required
def edit_product(request, pid):
    product = Product.objects.get(pid=pid)
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect('useradmin:edit-product', product.pid)
    else:
        form = AddProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
    }

    return render(request, "useradmin/edit-product.html", context)


@admin_required
def delete_product(request, pid):
    product = Product.objects.get(pid=pid)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('useradmin:products')


def orders(request):
    orders = CartOrder.objects.all()

    context = {
        'orders': orders,
    }

    return render(request, "useradmin/orders.html", context)


@admin_required
def order_detail(request, id):
    order = CartOrder.objects.get(id=id)
    order_items = CartOrderItems.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,
    }

    return render(request, "useradmin/order_detail.html", context)


@admin_required
@csrf_exempt
def change_order_status(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if request.method == 'POST':
        status = request.POST.get('status')
        status = status.capitalize()
        order.product_status = status
        order.save()
        messages.success(request, f"Order status changed to {status}!")

    return redirect('useradmin:order-detail', order.id)


@admin_required
def shop_page(request):
    products = Product.objects.all()
    revenue = CartOrder.objects.aggregate(price=Sum('price'))
    total_sales = CartOrderItems.objects.filter(order__paid_status=True).aggregate(qty=Sum('quantity'))

    context = {
        'products': products,
        'revenue': revenue,
        'total_sales': total_sales,
    }

    return render(request, "useradmin/shop_page.html", context)


@admin_required
def reviews(request):
    reviews = ProductReview.objects.all()

    context = {
        'reviews': reviews,
    }

    return render(request, "useradmin/reviews.html", context)


@admin_required
def settings(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        bio = request.POST.get('bio')
        address = request.POST.get('address')
        country = request.POST.get('country')

        if image != None:
            profile.image = image

        profile.full_name = full_name
        profile.phone = phone
        profile.bio = bio
        profile.address = address
        profile.country = country

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('useradmin:settings')

    context = {
        'profile': profile,
    }
    return render(request, "useradmin/settings.html", context)


@admin_required
def change_password(request):
    user = request.user

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if confirm_new_password != new_password:
            messages.warning(request, "Password does not match!")
            return redirect('useradmin:change_password')

        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully!")
            return redirect('useradmin:change_password')
        else:
            messages.warning(request, "Old Password Is Incorrect!")
            return redirect('useradmin:change_password')
    return render(request, "useradmin/change_password.html")













