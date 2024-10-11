from django.contrib import admin
from core.models import Category, Tags, Coupon, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, WishList, Address


class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages


class ProductsAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'products_image', 'price', 'category', 'vendor', 'featured', 'product_status', 'pid']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']


class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image']


class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status', 'sku']


class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_num', 'item', 'image', 'quantity', 'price', 'total']


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'review', 'date']


class WishListAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']


class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status']


admin.site.register(Product, ProductsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
