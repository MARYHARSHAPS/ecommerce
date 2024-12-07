from shop.models import Category,Product
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views
def categories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,"categories.html",context)

def allproducts(request,p):     #here p receives the category id
    c=Category.objects.get(id=p)        #reads a particular category object using id
    p=Product.objects.filter(category=c)        #reads all products under a particular category object
    context={'cat':c,'product':p}
    return render(request,"products.html",context)

def productdetails(request,p):
    pro=Product.objects.get(id=p)
    context={'product':pro}
    return render(request,"detail.html",context)

def register(request):
    if(request.method=="POST"):
        u=request.POST['u']
        p=request.POST['p']
        cp=request.POST['cp']
        f=request.POST['f']
        l=request.POST['l']
        e=request.POST['e']
        if(p==cp):
            u=User.objects.create_user(username=u,password=p,email=e,first_name=f,last_name=l)
            u.save()
            return redirect("shop:categories")
        else:
            return HttpResponse("passwords doesn't match")
    return render(request,"registration.html")


def user_login(request):
    if(request.method=="POST"):
        u=request.POST['u']
        p=request.POST['p']
        user=authenticate(username=u,password=p)     #checking if there is any matching user
        if user:                                        #if matching user exists
            login(request,user)
            return redirect("shop:categories")
        else:                                           #if no matching user
            return HttpResponse("Invalid credentials")
    return render(request,"login.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect('shop:login')


def addstock(request,p):
    product=Product.objects.get(id=p)
    if(request.method=='POST'):
        product.stock=request.POST['n']
        product.save()
        return redirect('shop:details',p)

    context={'pro':product}

    return render(request,"addstock.html",context)