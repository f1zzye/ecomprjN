from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from core.models import Category, Tags, Vendor, Coupon, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, WishList, Address
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.core import serializers
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator

import calendar
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth, ExtractYear
import stripe
from liqpay.liqpay import LiqPay
import base64
import hashlib
import json

from aiogram import Bot, exceptions


def index(request):
    # products = Product.objects.all().order_by('-id')
    products = Product.objects.filter(product_status='published', featured=True)

    context = {
        'products': products,
    }
    return render(request, 'core/index.html', context)


def product_list(request):
    products = Product.objects.filter(product_status='published')

    context = {
        'products': products,
    }
    return render(request, 'core/product-list.html', context)


def category_list(request):
    # categories = Category.objects.all()
    categories = Category.objects.all().annotate(product_count=Count('category'))

    context = {
        'categories': categories,
    }
    return render(request, 'core/category-list.html', context)


def category_product_list(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status='published', category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'core/category-product-list.html', context)


def vendor_list(request):
    vendors = Vendor.objects.all()

    context = {
        'vendors': vendors,
    }
    return render(request, 'core/vendor-list.html', context)


def vendor_details(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(product_status='published', vendor=vendor)

    context = {
        'vendor': vendor,
        'products': products,
    }
    return render(request, 'core/vendor-details.html', context)


def products_detail(request, pid):
    product = Product.objects.get(pid=pid)
    # product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)[:4]

    # getting reviews
    reviews = ProductReview.objects.filter(product=product).order_by('-date')

    # getting average reviews related to products
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # product review form
    review_form = ProductReviewForm

    make_review = True
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False

    p_image = product.p_images.all()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'make_review': make_review,
        'average_rating': average_rating,
        'p_image': p_image,
        'products': products,
    }
    return render(request, 'core/product-detail.html', context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status='published').order_by('-id')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        'products': products,
        'tag': tag,
    }
    return render(request, 'core/tag.html', context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST['review'],
        rating=request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
        'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )


def search(request):
    query = request.GET.get("query")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def filter_products(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')

    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status='published').order_by('-date').distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string('core/async/product-list.html', {'products': products})
    return JsonResponse({'data': data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'quantity': request.GET['quantity'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:

            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['quantity'] = int(cart_product[str(request.GET['id'])]['quantity'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})


def cart(request):
    cart_total = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total += float(item['price']) * int(item['quantity'])
        return render(request, 'core/cart.html', {'cart_data': request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total': cart_total})

    else:
        messages.warning(request, 'Your cart is empty')
        return redirect('core:index')


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total += float(item['price']) * int(item['quantity'])

    context = render_to_string('core/async/cart-list.html', {'cart_data': request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total': cart_total})
    return JsonResponse({'data': context, 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total': cart_total})


def update_cart(request):
    product_id = str(request.GET['id'])
    product_quantity = request.GET['quantity']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['quantity'] = product_quantity
            request.session['cart_data_obj'] = cart_data

    cart_total = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total += float(item['price']) * int(item['quantity'])

    context = render_to_string('core/async/cart-list.html', {'cart_data': request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total': cart_total})
    return JsonResponse({'data': context, 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total': cart_total})


def save_checkout_info(request):
    cart_total = 0
    total_amount = 0

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')

        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country

        if 'cart_data_obj' in request.session:

            for product_id, item in request.session['cart_data_obj'].items():
                total_amount += float(item['price']) * int(item['quantity'])

            if request.user.is_authenticated:
                user = request.user
            else:
                user = None

            order = CartOrder.objects.create(
                user=user,
                price=total_amount,
                full_name=full_name,
                email=email,
                phone=mobile,
                address=address,
                city=city,
                state=state,
                country=country,
            )

            del request.session['full_name']
            del request.session['email']
            del request.session['mobile']
            del request.session['address']
            del request.session['city']
            del request.session['state']
            del request.session['country']

            for product_id, item in request.session['cart_data_obj'].items():
                cart_total += float(item['price']) * int(item['quantity'])

                cart_order_products = CartOrderItems.objects.create(
                    order=order,
                    invoice_num='INVOICE_№-' + str(order.id),
                    item=item['title'],
                    image=item['image'],
                    quantity=item['quantity'],
                    price=item['price'],
                    total=float(item['price']) * int(item['quantity']),
                )

        return redirect('core:checkout', order.oid)
    return redirect('core:checkout', order.oid)


@login_required()
def checkout(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = CartOrderItems.objects.filter(order=order)

    if request.method == 'POST':
        code = request.POST.get('code')
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, 'Coupon already activated')
                return redirect('core:checkout', order.oid)
            else:
                discount = order.price * coupon.discount / 100

                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()

                messages.success(request, 'Coupon Activated')
                return redirect('core:checkout', order.oid)
        else:
            messages.warning(request, 'Coupon Does Not Exists')
            return redirect('core:checkout', order.oid)

    # Инициализация LiqPay
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    params = {
        'action': 'pay',
        'amount': str(order.price),
        'currency': 'USD',
        'description': f'Payment for order {order.oid}',
        'order_id': order.oid,
        'version': '3',
        'sandbox': 0,  # Удалите эту строку для продакшн-режима
        # 'server_url': request.build_absolute_uri(reverse("core:liqpay_callback")),
        'server_url': request.build_absolute_uri('https://f633-62-16-0-185.ngrok-free.app/billing/pay-callback/'),
        'result_url': request.build_absolute_uri(reverse("core:payment-result", args=[order.oid]))
    }
    form_html = liqpay.cnb_form(params)

    context = {
        'order': order,
        'order_items': order_items,
        'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
        'form_html': form_html,
    }
    return render(request, 'core/checkout.html', context)


@csrf_exempt
def liqpay_callback(request):
    print('Callback function entered')
    data = request.POST.get('data')
    signature = request.POST.get('signature')
    print('Data:', data)
    print('Signature:', signature)

    sign_str = settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY
    sign = base64.b64encode(hashlib.sha1(sign_str.encode('utf-8')).digest()).decode('utf-8')
    print('Generated Sign:', sign)

    if sign != signature:
        print('Invalid callback signature')
        return HttpResponse(status=400)

    decoded_data = base64.b64decode(data).decode('utf-8')
    response = json.loads(decoded_data)
    print('Callback data:', response)

    try:
        order = CartOrder.objects.get(oid=response['order_id'])
    except CartOrder.DoesNotExist:
        print('Order not found')
        return HttpResponse(status=404)

    if response['status'] == 'success':
        order.paid_status = True
        order.save()
    elif response['status'] == 'failure':
        print('Payment failed')
    elif response['status'] in ['sandbox', 'wait_accept', 'processing', 'wait_secure']:
        print('Payment status:', response['status'])
    else:
        print('Unknown payment status:', response['status'])

    return HttpResponse()


def payment_result(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    if order.paid_status:
        return redirect('core:payment-completed', oid=oid)
    else:
        return redirect('core:payment-failed', oid=oid)


# @method_decorator(csrf_exempt, name='dispatch')
# class PayCallbackView(View):
#     def post(self, request, *args, **kwargs):
#         liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
#         data = request.POST.get('data')
#         signature = request.POST.get('signature')
#         sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
#         if sign == signature:
#             print('callback is valid')
#         response = liqpay.decode_data_from_str(data)
#         print('callback data', response)
#         if response['status'] == 'success':
#             order = CartOrder.objects.get(oid=response['order_id'])
#             order.paid_status = True
#             order.save()
#         return HttpResponse()


@login_required()
def payment_details(request, oid):
    order = CartOrder.objects.get(oid=oid)
    cart_total = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total += float(item['price']) * int(item['quantity'])
    cart_total -= float(order.saved)
    context = {
        'order': order,
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total': cart_total,
        'saved': order.saved,
    }
    return render(request, 'core/payment-details.html', context)


@csrf_exempt
def create_checkout_session(request, oid):
    order = CartOrder.objects.get(oid=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email=order.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("core:payment-failed"))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})


@login_required
def payment_completed(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if order.paid_status == False:
        order.paid_status = True
        order.save()

    context = {
        'order': order,
    }

    return render(request, 'core/payment-completed.html', context)


@login_required
def payment_failed(request, oid):
    return render(request, 'core/payment-failed.html')


@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by('-order_date')
    address = Address.objects.filter(user=request.user)

    profile = Profile.objects.get(user=request.user)

    orders = CartOrder.objects.annotate(month=ExtractMonth('order_date')).values('month').annotate(count=Count('id')).values('month', 'count')
    month = []
    total_orders = []

    for order in orders:
        month.append(calendar.month_name[order['month']])
        total_orders.append(order['count'])

    if request.method == 'POST':
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, 'Address has been added successfully.')
        return redirect('core:dashboard')

    context = {
        'profile': profile,
        'orders_list': orders_list,
        'address': address,
        'orders': orders,
        'month': month,
        'total_orders': total_orders,
    }
    return render(request, 'core/dashboard.html', context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)

    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({'boolean': True})


@login_required()
def wishlist(request):
    wishlist = WishList.objects.filter(user=request.user)
    wishlist_count = wishlist.count()

    context = {
        'wishlist': wishlist,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'core/wishlist.html', context)


def add_to_wishlist(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)

    context = {}

    wishlist_count = WishList.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            'bool': True
        }
    else:
        new_wishlist = WishList.objects.create(
            product=product,
            user=request.user,
        )
        context = {
            'bool': True
        }
    return JsonResponse(context)


def delete_from_wishlist(request):
    pid = request.GET['id']
    wishlist = WishList.objects.filter(user=request.user)

    product = WishList.objects.get(id=pid)
    product.delete()

    wishlist_count = wishlist.count()

    context = {
        'bool': True,
        'wishlist': wishlist,
    }
    wishlist_json = serializers.serialize('json', wishlist)
    data = render_to_string('core/async/wishlist-list.html', context)
    return JsonResponse({'data': data, 'wishlist': wishlist_json, 'wishlist_count': wishlist_count})


def contact(request):
    return render(request, 'core/contact.html')


def ajax_contact(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )
    context = {
        'bool': True,
        'message': 'Your message has been sent successfully.'
    }
    return JsonResponse({'context': context})


def about_us(request):
    return render(request, 'core/about-us.html')


def purchase_guide(request):
    return render(request, 'core/purchase-guide.html')


def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')


def terms_of_service(request):
    return render(request, 'core/terms-of-service.html')














