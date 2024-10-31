from django.http import HttpResponse
from django.shortcuts import render,redirect
from shop.models import Category,Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.
def allcategories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,'category.html',context)

def allproducts(request,p):
    c=Category.objects.get(id=p)
    p=Product.objects.filter(category=c)
    context={'cat':c,'product':p}
    return render(request,'product.html',context)

def alldetails(request,p):
    d=Product.objects.get(id=p)
    context={'product':d}
    return render(request,'details.html',context)

def register(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        c = request.POST['c']

        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']




        if c == p:
            user = User.objects.create_user(username=u, password=p, first_name=f, last_name=l,email=e)
            user.save()

        return redirect('shop:categories')
    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        print(u,p)
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('shop:categories')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')



def user_logout(request):
    logout(request)
    return redirect('shop:categories')

def add_stock(request,p):
    product=Product.objects.get(id=p)
    if request.method=="POST":
        product.stock=request.POST['s']
        product.save()
        return redirect('shop:categories')
    context={'product':product}
    return render(request,'addstock.html',context)


