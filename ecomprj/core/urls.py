from django.urls import path, include
from core.views import index, contact, ajax_contact, create_checkout_session, payment_details, delete_from_wishlist, payment_result, liqpay_callback, add_to_wishlist, wishlist, make_address_default, order_detail, customer_dashboard, payment_completed, payment_failed, checkout, update_cart, delete_item_from_cart, search, cart, add_to_cart, ajax_add_review, filter_products, product_list, category_list, category_product_list, vendor_list, vendor_details, products_detail, tag_list
from core import views

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('products/', product_list, name='product-list'),
    path('product/<pid>/', products_detail, name='product-detail'),

    path('category/', category_list, name='category-list'),
    path('category/<cid>/', category_product_list, name='category-product-list'),

    path('vendors/', vendor_list, name='vendor-list'),
    path('vendor/<vid>/', vendor_details, name='vendor-details'),

    path('products/tag/<slug:tag_slug>/', tag_list, name='tags'),
    path('search/', search, name='search'),

    path('ajax-add-review/<int:pid>/', ajax_add_review, name='ajax-add-review'),

    path('filter-products/', filter_products, name='filter-products'),

    # filter product
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('cart/', cart, name='cart'),

    path('delete-from-cart/', delete_item_from_cart, name='delete-from-cart'),
    path('update-cart/', update_cart, name='update-cart'),

    path('checkout/<oid>/', checkout, name='checkout'),

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-failed/<str:oid>/', payment_failed, name='payment-failed'),
    path('payment-completed/<oid>/', payment_completed, name='payment-completed'),

    path('dashboard/', customer_dashboard, name='dashboard'),

    path('dashboard/order/<int:id>', order_detail, name='order-detail'),

    path("make-default-address/", make_address_default, name="make-default-address"),

    path("wishlist/", wishlist, name="wishlist"),
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),
    path("delete-from-wishlist/", delete_from_wishlist, name="delete-from-wishlist"),

    # other urls
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact, name="ajax-contact-form"),

    # new Route
    path("save_checkout_info/", views.save_checkout_info, name="save_checkout_info"),
    path("api/create_checkout_session/<oid>/", create_checkout_session, name="api_checkout_session"),

    path('payment-details/<oid>/', payment_details, name='payment-details'),

    path('create-checkout-session/<str:oid>/', create_checkout_session, name='create_checkout_session'),
    path('payment-completed/<str:oid>/', payment_completed, name='payment-completed'),
    path('billing/pay-callback/', liqpay_callback, name='liqpay_callback'),

    path('payment-result/<str:oid>/', payment_result, name='payment-result'),

    path('verify_mfa/', views.verify_mfa, name='verify_mfa'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
]