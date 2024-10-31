from itertools import product

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from cart.models import Cart,Payment,Order_details
from django.views.decorators.csrf import csrf_exempt
from razorpay import Client
from shop.models import Product,Category

from django.contrib.auth.models import User
from django.contrib.auth import login
import razorpay
from unicodedata import category


# Create your views here.
@login_required
def add_to_cart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            c.quantity+=1
            c.save()
            p.stock-=1
            p.save()
    except:
        if(p.stock>0):
            c=Cart.objects.create(product=p,user=u,quantity=1)
            c.save()
            p.stock-=1
            p.save()

    return redirect('cart:cartview')

@login_required
def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)
    for i in c:
        total+=i.quantity*i.product.price
    context={'cart':c,'total':total}
    return render(request,'cart.html',context)

def cart_remove(request,i):
    p=Product.objects.get(id=i)
    u=request.user

    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()
        else:
            c.delete()
    except:
        return redirect('cart:cartview')

@login_required
def cart_delete(request,i):
    u=request.user
    p=Product.objects.get(id=i)
    try:
        c=Cart.objects.get(user=u,product=p)
        c.delete()
        p.stock+=c.quantity
        p.save()
    except:
        pass
    return redirect('cart:cartview')

@login_required
def orderform(request):
    if(request.method=="POST"):
        address=request.POST['a']
        phoneno = request.POST['p']
        pin = request.POST['pi']

        u=request.user

        c=Cart.objects.filter(user=u)

        total=0

        for i in c:
            total+=i.quantity*i.product.price
        total=int(total*100)
        client=razorpay.Client(auth=('rzp_test_pmPSaVlRqWPJtD','S4ZHOmym9wlTbYNV8Z8nWqXg'))
        response_payment=client.order.create(dict(amount=total,currency="INR"))
        # print(response_payment)
        order_id=response_payment['id']
        order_status=response_payment['status']
        if(order_status=="created"):
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phoneno=phoneno,pin=pin,order_id=order_id)
                o.save()
        else:
            pass
        response_payment['name']=u.username
        context={'payment':response_payment}
        return render(request, 'payment.html',context)
    return render(request,'orderform.html')

@csrf_exempt
def payment_status(request,u):
    user = User.objects.get(username=u)
    if(not request.user.is_authenticated):
        login(request,user)

    if(request.method=="POST"):
        response=request.POST
        print(response)

        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        client=razorpay.Client(auth=('rzp_test_pmPSaVlRqWPJtD','S4ZHOmym9wlTbYNV8Z8nWqXg'))
        try:
            status=client.utility.verify_payment_signature(param_dict)
            print(status)

            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()



            o=Order_details.objects.filter(user=user,order_id=response['razorpay_order_id'])
            for i in o:

                 i.payment_status="paid"
                 i.save()

            c=Cart.objects.filter(user=user)
            c.delete()

        except:
            pass
    return render(request,'payment_status.html',{'status':status})

def yourorder(request):
    u=request.user

    o=Order_details.objects.filter(user=u,payment_status="paid")
    context={'order_details':o}
    return render(request,'yourorder.html',context)

def add_category(request):
    if request.method == "POST":
        n = request.POST['n']
        d = request.POST['d']
        i = request.FILES['i']
        c=Category.objects.create(name=n,desc=d,image=i)
        c.save()
        return redirect('shop:categories')


    return render(request,'addcategory.html')

def add_product(request):
    if request.method == "POST":
        n = request.POST['n']
        d = request.POST['d']
        p = request.POST['p']
        s = request.POST['s']

        i = request.FILES['i']
        c=request.POST['c']
        cat=Category.objects.get(name=c)
        p=Product.objects.create(name=n,desc=d,price=p,stock=s,image=i,category=cat)
        p.save()
        return redirect('shop:categories')

    return render(request,'addproduct.html')







