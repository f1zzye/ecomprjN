from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, WishList, Address
from django.db.models import Min, Max
from django.contrib import messages


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    min_max_price = Product.objects.aggregate(Min('price'), Max('price'))

    try:
        wishlist = WishList.objects.filter(user=request.user)
    except:
        messages.warning(request, 'You need to login before accessing your wishlist.')
        wishlist = 0


    try:
         address = Address.objects.get(user=request.user)
    except:
        address = None

    return {
        'vendors': vendors,
        'wishlist': wishlist,
        'categories': categories,
        'address': address,
        'min_max_price': min_max_price,
    }










