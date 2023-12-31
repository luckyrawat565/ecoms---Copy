from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse, JsonResponse
from uuid import UUID
from django.contrib import messages
import razorpay
from.models import Product, ProductVariants, Image, Category, Size, ColorVariants, Stock
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Cart, CartItem
from django.db.models import Sum
import json
from accounts import utils
from accounts.models import address
from decimal import Decimal
from django.db.models.functions import Coalesce
from collections import defaultdict








def calculate_variant_prices(cart):
    variant_info = defaultdict(lambda:{'discount_price':0, 'total_price':0,'variant':''})
    cart_items = CartItem.objects.filter(cart = cart)

    for cart_item in cart_items:
        variant = cart_item.stock_variant
        quantity = cart_item.quantity
        price_per_variant = variant.variant.price.price
        price_per_variant_discount = variant.variant.price.sale_price

        variant_info[variant]['discount_price'] += price_per_variant_discount * quantity
        variant_info[variant]['total_price'] += quantity * price_per_variant
        variant_info[variant]['variant'] = variant
    
    return variant_info


# Create your views here.
def index(request):
    categories = Category.objects.all()
    categories_with_variants = []

    for category in categories:
        products = Product.objects.filter(category = category)
        print("products is : ", products)
        representative_variants = []

        for product in products:
            representative_variant = ProductVariants.objects.filter(product = product).order_by('price').first()
            print('\nrepresentative variants is : ', representative_variant)
            if representative_variant:
                representative_variants.append(representative_variant)
            

        print('representative vairsnt : ', representative_variants)
        if representative_variants:
            categories_with_variants.append({'category':category, 'variants':representative_variants})

    print('categoresi with variatn si s: ',categories_with_variants)
    return render(request, 'app/tem.html',{'categories_with_variants':categories_with_variants})  
    # return render(request, "app/home.html", {'categories':categories, 'products_by_category':products_by_cat})




def product_details(request, slug):
    try:
        
        variant = get_object_or_404(ProductVariants, slug = slug)        
        stocks = Stock.objects.filter(variant = variant)
        related_sizes = Size.objects.all()
        related_variant = ProductVariants.objects.filter(product = variant.product).prefetch_related('color')                                                
        print('related_size is ',related_sizes)
        return render(request, 'app/product-details.html', {"variant":variant, 'related_variants':related_variant,'variant_sizes':set(related_sizes),'stocks':stocks})        
        
    

    except Exception as e:
        print(e)
    
    return render(request, 'app/home.html')


def add_to_cart(request):    
    variant_uid = request.POST.get('variant_id')
    color = request.POST.get('color')            
    size = request.POST.get('sizes')                
    variant_redirect = ProductVariants.objects.filter(uid = variant_uid)[0]
    
    
    variant_stock = Stock.objects.filter(variant = variant_uid, sizes=size, colors = color)
    print(variant_stock)
        
    if variant_stock.exists():
        if variant_stock[0].stock_quantity > 0:
            if request.user.is_authenticated:
                user_cart, created = Cart.objects.get_or_create(user=request.user)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                user_cart, created = Cart.objects.get_or_create(session_key=session_key)
    
            
            cart_item, created = CartItem.objects.get_or_create(cart=user_cart, stock_variant = variant_stock[0])
            cart_item.quantity += 1
            
            
            cart_item.save()

            messages.success(request, f"{variant_redirect.product.name} added to cart.")
        else:
            messages.success(request, "out of stock")     
        return redirect('product/'+variant_redirect.slug)     
    else:
        messages.success(request,"not available")
        return redirect('product/'+variant_redirect.slug)
                                  
    


def view_cart(request):        

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart , createad = Cart.objects.get_or_create(user = request.user)
    else:
        # Retrieve or create a cart using session ID
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        cart_items = cart.cart_items.all()
    

    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        action = request.POST.get('action')

        if variant_id and action:            
            cart_item = CartItem.objects.filter(stock_variant = variant_id).first()

            if action == 'add':
                if cart_item:
                    cart_item.quantity +=1
                    print("\n\n\nn\n add is in progress \n\n\n\n\n")
                    cart_item.save()
                else:
                    CartItem.objects.create(cart = cart, stock_variant = variant_id, quantity = 1)
                    
            elif action == 'decrease':
                if cart_item and cart_item.quantity> 1:
                    cart_item.quantity -=1
                    cart_item.save()
            elif action == 'remove':
                if cart_item:
                    cart_item.delete()

    
    variant_info = calculate_variant_prices(cart)
    
    return render(request, 'app/cart.html',{'cart_items':cart_items, 'variant_info':variant_info.values()})        


    

    


def payment_sucess(request):
    return HttpResponse(request, 'h1 payment sucessx')

@csrf_exempt  # Disable CSRF protection for this view (for demonstration purposes)
def sucess(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = CartItem.objects.all()
            cart.delete()
            # Process the received data as needed
            # For example, you can save it to a database
            
            print('i got data')             
            return redirect('app:index')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)


def user_address(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        street = request.POST.get('street')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip')
        landmark = request.POST.get('landmark')
        mobile = request.POST.get('mobile')
        alternate_mobile = request.POST.get('alternate_mobile')

        Address = address(user_profile = request.user.profile, street = street, state = state, 
                         city = city, postal_code = zip_code, landmark = landmark, mobile = mobile, alternate_mobile = alternate_mobile)
        
        Address.save()

        request.user.profile.address_filled = True
        request.user.profile.save()


        return redirect('/view_cart')
    return render(request, 'accounts/address_form.html')

def checkout(request):        
    discount = 0
    total_amount = 0
    total_discounted_price = 0
    size = 0

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(cart__user=request.user)
        cart , createad = Cart.objects.get_or_create(user = request.user)
    else:
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        cart_item = cart.cart_items.all()
            

    
    for cart_itm in cart_item:
        total_amount += cart_itm.stock_variant.variant.price.price * cart_itm.quantity        
        total_discounted_price += cart_itm.stock_variant.variant.price.sale_price * cart_itm.quantity
    

    variant_info = calculate_variant_prices(cart)
        
    user = request.user
    if utils.has_filled_address(user):

        if total_discounted_price > 0:        
            client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))        
            data = { "amount": int(total_discounted_price*100) , "currency": "INR", "receipt": "order_rcptid_11" }    
            payment = client.order.create(data=data)
            print("\n data is : ", payment)

            return render(request, 'app/checkout.html',{'cart_items':cart_item, 'total_price':total_amount, 'discount':total_amount - total_discounted_price, 'total_actual':total_discounted_price,'payment':payment ,'variant_info':variant_info.values()})
        return render(request, 'app/checkout.html',{'cart_items':cart_item, 'total_price':total_amount, 'discount':total_amount - total_discounted_price, 'total_actual':total_discounted_price ,'variant_info':variant_info.values()})    
        # return render(request, 'app/cart.html')
    else:
        return render(request, 'accounts/address_form.html')
            