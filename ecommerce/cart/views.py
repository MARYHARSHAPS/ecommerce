from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from shop.models import Product,Category
from cart.models import Cart, Payment, Order_details
from django.contrib.auth.decorators import login_required
import razorpay



# Create your views here.

@login_required
def addtocart(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:  #if particular product for a particular user already exist
        c = Cart.objects.get(product=p, user=u)
        if (p.stock > 0):
            c.quantity += 1
            c.save()
            p.stock -= 1
            p.save()

    except:  #if particular record does not exist
        if (p.stock > 0):
            c = Cart.objects.create(product=p, user=u, quantity=1)
            c.save()
            p.stock -= 1
            p.save()

    return redirect('cart:cart')


@login_required
def cart_view(request):
    u = request.user
    total = 0
    c = Cart.objects.filter(user=u)  #all cart items for a particular user
    total = 0
    for i in c:
        total += i.quantity * i.product.price
    context = {'cart': c, 'total': total}
    return render(request, "cart.html", context)


@login_required
def cart_remove(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:  #if particular product for a particular user already exist
        c = Cart.objects.get(product=p, user=u)
        if (c.quantity > 1):
            c.quantity -= 1
            c.save()
            p.stock += 1
            p.save()
        else:
            c.delete()
            p.stock += 1
            p.save()
    except:
        pass
    return redirect('cart:cart')


@login_required
def cart_delete(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:  #if particular product for a particular user already exist
        c = Cart.objects.get(product=p, user=u)
        c.delete()
        p.stock += c.quantity
        p.save()
    except:
        pass
    return redirect('cart:cart')


def orderform(request):
    if (request.method == "POST"):
        address = request.POST['a']
        phone = request.POST['p']
        pin = request.POST['pi']
        u = request.user
        c = Cart.objects.filter(user=u)
        for i in c:
            total = i.quantity * i.product.price
        total1 = int(total * 100)

        client = razorpay.Client(
            auth=('rzp_test_ZlheBIERsxt6Dt', 'FThMLu6K2AWckJF6mvr4KxdO'))  #creates a client connection
        #using razorpay id and secret code

        response_payment = client.order.create(dict(amount=total1, currency="INR"))  #creates an order with razorpay
        # using razorpay client

        print(response_payment)

        order_id = response_payment['id']
        status = response_payment['status']

        if (status == "created"):
            p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
            p.save()
            for i in c:
                o = Order_details.objects.create(product=i.product, user=u, no_of_items=i.quantity, address=address,
                                                 phone_no=phone, pin=pin, order_id=order_id)
                o.save()
        response_payment['name'] = u.username
        context = {'payment': response_payment}
        return render(request, "payment.html", context)

    return render(request, "order.html")


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def payment_status(request, u):
    u = User.objects.get(username=u)
    if not request.user.is_authenticated:
        login(request,u)
    if (request.method == "POST"):
        response = request.POST
        print(response)

        param_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        client = razorpay.Client(
            auth=('rzp_test_ZlheBIERsxt6Dt', 'FThMLu6K2AWckJF6mvr4KxdO'))  #to create razorpay client
        print(client)
        try:
            status = client.utility.verify_payment_signature(param_dict)  #to check the authenticity of razorpay signature
            print(status)

            #to retrieve a particular record from payment table matching with razorpay response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()

            # to retrieve a record from order_details table matching with razorpay response order id
            o=Order_details.objects.filter(order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status="completed"
                i.save()


            c=Cart.objects.filter(user=u)   #filter all record matching with particular user
            c.delete()



        except:
            pass

    return render(request, "payment_status.html",{'status':status})


@login_required
def order_view(request):
    u=request.user
    o=Order_details.objects.filter(user=u)
    print(o)
    context={'orders':o}
    return render(request,"orderview.html",context)


def addcategories(request):
    if(request.method=='POST'):
        n=request.POST['n']
        i=request.FILES['i']
        d=request.POST['d']
        c=Category.objects.create(name=n,image=i,description=d)
        c.save()
        return redirect('shop:categories')
    return render(request,"addcategories.html")


def addproducts(request):
    if (request.method == 'POST'):
        n = request.POST['n']
        i = request.FILES['i']
        d = request.POST['d']
        s = request.POST['s']
        p = request.POST['p']
        c = request.POST['c']

        cat=Category.objects.get(name=c)
        p = Product.objects.create(name=n,image=i,desc=d,price=p,stock=s,category=cat)
        p.save()
        return redirect('shop:categories')
    return render(request,"addproducts.html")

