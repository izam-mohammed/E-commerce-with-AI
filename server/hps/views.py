from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from hps.models import *
from django.http import JsonResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.core.mail import send_mail
from django.template.loader import get_template
from weasyprint import HTML


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    cat=Category.objects.filter(cat_status=True)
    brd=Brand.objects.filter(brd_status=True)
    prd=PrdVariation.objects.select_related('prd_id__brd_id').filter(prd_status=True)
    ban=Banner.objects.filter(status=True)
    context={'cat':cat,'brd':brd,'prd':prd,'ban':ban}
    return render(request,"user/index.html",context)

    
def register(request):
    if request.method == 'POST':
        uname=request.POST['uname']
        uemail=request.POST['uemail']
        upass=request.POST['upass']
        cpass=request.POST['cpass']
        if(upass!=cpass):
            messages.info(request,'Password does not match.')
            
        elif User.objects.filter(username=uname).exists():
            messages.info(request,'Username already exists.')
        elif User.objects.filter(email=uemail).exists():
            messages.info(request,'Email is taken.')
            
        else:
            new_user=User.objects.create_user(username=uname,email=uemail,password=upass)
            new_user.save()
            get_user=User.objects.get(email=uemail)
            new_wallet=Wallet(balance=0,user_id=get_user.id)
            new_wallet.save()
            return redirect('index')
    return render(request,"user/register.html")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect(index)
    if request.method=="POST":
        uname=request.POST.get("uname")
        upass=request.POST.get("upass")
        myuser=authenticate(username=uname,password=upass)
        if myuser is not None:
            login(request,myuser)
            # messages.success(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentails")
            return redirect('user_login')
    return render(request,"user/login.html")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)      
def user_logout(request):
    if('coupon' in request.session):
        del request.session['coupon']
    logout(request)
    # messages.info(request,"Logout Success")
    return redirect('/')

def view_prod(request,pid):
    cat=Category.objects.filter(cat_status=True)
    brd=Brand.objects.filter(brd_status=True)
    prd=PrdVariation.objects.get(id=pid) # selected product data
    prd1=PrdVariation.objects.get(id=pid) # to get prd_id for product variation
    prdt=PrdVariation.objects.filter(prd_id_id=prd1.prd_id_id) # display other product variations
    if request.user.is_authenticated:
        ch_pr=Cart.objects.filter(prd_var=pid,user=request.user,val=False)
        wl_pr=Wishlist.objects.filter(item=pid,user=request.user)
    # pdimg=PrdImage.objects.get(prd_id=pid)
        context={'cat':cat,'prd':prd,'prdt':prdt,'ch_pr':ch_pr,'wl_pr':wl_pr,'brd':brd}
        return render(request,"user/product.html",context)
    context={'cat':cat,'prd':prd,'prdt':prdt,'brd':brd}
    return render(request,"user/product.html",context)

def brand_wise(request,bid):
    prd=PrdVariation.objects.filter(prd_id__brd_id=bid)
    cat=Category.objects.filter(cat_status=True)
    brd=Brand.objects.filter(brd_status=True)
    context={'cat':cat,'brd':brd,'prd':prd}
    return render(request,"user/index.html",context)

def cat_wise(request,cid):
    prd=PrdVariation.objects.filter(prd_id__cat_id=cid)
    cat=Category.objects.filter(cat_status=True)
    brd=Brand.objects.filter(brd_status=True)
    context={'cat':cat,'brd':brd,'prd':prd}
    return render(request,"user/index.html",context)

def search_result(request):
    cat=Category.objects.filter(cat_status=True)
    brd=Brand.objects.filter(brd_status=True)
    if request.method=="POST":
        s_value=request.POST["s_value"]
        if Category.objects.filter(cat_name__iexact=s_value).exists():
            s_cat=Category.objects.get(cat_name__iexact=s_value).id
            s_prd=Product.objects.filter(cat_id_id=s_cat).values_list('id', flat=True)
            prd=PrdVariation.objects.filter(prd_id_id__in=s_prd)
            context={'cat':cat,'brd':brd,'prd':prd}
            return render(request,"user/index.html",context)
        elif Brand.objects.filter(brd_name__iexact=s_value).exists():
            s_brd=Brand.objects.get(brd_name__iexact=s_value).id
            s_prd=Product.objects.filter(brd_id_id=s_brd).values_list('id', flat=True)
            prd=PrdVariation.objects.filter(prd_id_id__in=s_prd)
            context={'cat':cat,'brd':brd,'prd':prd}
            return render(request,"user/index.html",context)
        elif Product.objects.filter(prd_name__iexact=s_value).exists():
            s_prd=Product.objects.get(prd_name__iexact=s_value).id
            print(s_prd)
            prd=PrdVariation.objects.filter(prd_id_id=s_prd)
            context={'cat':cat,'brd':brd,'prd':prd}
            return render(request,"user/index.html",context)
    context={'cat':cat,'brd':brd,'prd':prd}
    return render(request,"user/index.html",context)    
        
        
def cart(request):
    cur_user=request.user
    crt=Cart.objects.filter(user=cur_user,val=False).select_related('prd_id')
    print(crt.query)
    tot=0
    for p in crt:
        tot=tot+p.prd_var.cur_price * p.qty
    context={'crt':crt,'tot':tot}
    return render(request,"user/cart1.html",context)
    
def add_add(request):
    if request.user.is_authenticated:
        cur_user=request.user
        if request.method == "POST":
            name=request.POST['name'] 
            addr=request.POST['addr'] 
            pin=request.POST['pin'] 
            ph_no=request.POST['ph_no'] 
            area=request.POST['area'] 
            city=request.POST['city'] 
            state=request.POST['state'] 
            type=request.POST['type']
            new_add=Address(user=cur_user,name=name,addr=addr,pin=pin,ph_no=ph_no,area=area,city=city,state=state,type=type)
            new_add.save()
            return redirect(view_add)
    else:
        return redirect(login)

    
def view_add(request):
    if request.user.is_authenticated:
        cur_user=request.user
        adds=Address.objects.filter(user=cur_user,remove_address=True)
        return render(request,"user/add_add.html",{'adds':adds})
    else:
        return redirect(user_login)

def add_cart(request,pid):
    if request.user.is_authenticated:
        cur_user=request.user
        prd=PrdVariation.objects.get(id=pid)
        prdt=Product.objects.get(id=prd.prd_id_id)
        prd.stock-=1
        prd.save()
        crt=Cart(prd_id_id=prdt.id,prd_var_id=pid,user=cur_user,qty=1)
        crt.save()
        return redirect(cart)  
    else:
        return redirect(user_login)
    
def rem_cart(request,cid):
    crt=Cart.objects.get(id=cid,val=False)
    crt.delete()
    return redirect(cart)

def inc_qty(request, item_id):
    cart_item = Cart.objects.get(id=item_id,val=False)
    prd=PrdVariation.objects.get(id=cart_item.prd_var_id)
    print(prd)
    if(prd.stock>0):
        cart_item.qty += 1
        cart_item.save()
        prd.stock-=1
        prd.save()
        cur_user=request.user
        crt=Cart.objects.filter(user=cur_user,val=False)
        tot=0
        for p in crt:
            tot=tot+p.prd_var.cur_price * p.qty
        context={'new_qty': cart_item.qty,'price':cart_item.prd_var.cur_price,'tot':tot,'Success':True}
        return JsonResponse(context)
    else:
        context={'Success':False}
        return JsonResponse(context)
    
def dec_qty(request, item_id):
    cart_item = Cart.objects.get(id=item_id,val=False)
    prd=PrdVariation.objects.get(id=cart_item.prd_var_id)
    if cart_item.qty>1:
        cart_item.qty -= 1
        cart_item.save()
        prd.stock+=1
        prd.save()
    cur_user=request.user
    crt=Cart.objects.filter(user=cur_user)
    tot=0
    for p in crt:
        tot=tot+p.prd_var.cur_price * p.qty
    context={'new_qty': cart_item.qty,'price':cart_item.prd_var.cur_price,'tot':tot}
    return JsonResponse(context)

def checkout(request,ad_id):
    crt=Cart.objects.filter(user=request.user,val=False).select_related('prd_id')
    addr=Address.objects.get(id=ad_id)
    tot=0
    for p in crt:
        tot=tot+p.prd_var.cur_price * p.qty
    r_tot=tot*100
    pay_amount=tot
    if request.method == "POST":
        if request.POST.get("form_type") == 'apply':
            code=request.POST['code']
            if Coupon.objects.filter(code=code).exists():
                coupon_id=Coupon.objects.get(code=str(code)).id
                request.session['coupon']=coupon_id
                print(request.session['coupon'])
            else:
                messages.info(request,"Invalid Coupon")
        if request.POST.get("form_type") == 'cancel':
            del request.session['coupon']
    if('coupon' in request.session):
        value=Coupon.objects.get(id=request.session['coupon']).value
        pay_amount=tot-tot*(int(value)/100)
        print(pay_amount)
    coupons=Coupon.objects.filter(status=True)
    context={'crt':crt,'addr':addr,'tot':tot,'r_tot':r_tot,'coupons':coupons,'pay_amount':pay_amount}
    return render(request,"user/checkout.html",context)


def create_order(request,ad_id):
    crt=Cart.objects.filter(user=request.user,val=False)
    ord_list=[]
    item_list=[]
    tot=0
    for c in crt:  
        sub=c.qty*c.prd_var.cur_price
        tot+=sub
        ord_item=OrderItem(item=c.prd_var,qty=c.qty,sub_tot=sub)
        item=Product.objects.get(id=c.prd_id_id)
        item_list.append(item.prd_name)
        ord_item.save()
        c.val=True
        c.save()
        print(ord_item)
        ord_list.append(ord_item)
    if('coupon' in request.session):
        value=Coupon.objects.get(id=request.session['coupon']).value
        coupon_id=Coupon.objects.get(id=request.session['coupon']).id
        tot=tot-tot*(int(value)/100)
        new_order=Order.objects.create(user=request.user,tot_amount=tot,del_add_id=ad_id,coupon_apply_id=coupon_id,status="Pending")
        del request.session['coupon']
    else:
        new_order=Order.objects.create(user=request.user,tot_amount=tot,del_add_id=ad_id,status="Pending")
    item_string=' '.join(item_list)  
    notification_description="Your order containing "+item_string+" has been placed." 
    notify=Notification(description=notification_description,user=request.user)
    notify.save()
    for ord in ord_list:
        new_order.new_order.add(ord)
    new_order.save()
    or_id=new_order
    r_tot=new_order.tot_amount*100
    context={'or_id':or_id,'r_tot':r_tot}
    return render(request,"user/pay.html",context)

def cod_paid(request,or_id):
    new_order=Order.objects.get(id=or_id)
    new_order.pay_method="COD"
    new_order.status="Confirmed"
    new_order.save()
    context={'new_order':new_order}
    return render(request,"user/complete.html",context)

@csrf_exempt    
def r_paid(request,or_id):
    new_order=Order.objects.get(id=or_id)
    r_tot=new_order.tot_amount*100
    client = razorpay.Client(auth=("rzp_test_DLTeq2nNMzXQkj", "bmng64HRS0muDq1yCGX0m8YS"))
    payment=client.order.create({'amount':r_tot,'currency':"INR",'payment_capture':'1'})
    new_order.pay_method="Razor Pay"
    new_order.razor_pay_id = payment['id']
    new_order.status="Confirmed"
    new_order.save()
    context={'new_order':new_order,'payment':payment,'r_tot':r_tot}
    return render(request,"user/complete.html",context)

def orders(request):
    if request.user.is_authenticated:
        ord=Order.objects.filter(user_id=request.user).order_by('-id')
        return render(request,"user/orders.html",{'ord':ord})
    else:
        return redirect(user_login)
    
def ord_details(request,or_id):
    ord=Order.objects.get(id=or_id).new_order.all().select_related('item')
    total=0
    for o in ord:
        total+=o.sub_tot
    ord_data=Order.objects.get(id=or_id)
    addr=Address.objects.get(id=ord_data.del_add_id)
    if(ord_data.coupon_apply):
        coupon=Coupon.objects.get(id=ord_data.coupon_apply_id)
        context={'ord':ord,'addr':addr,'ord_data':ord_data,'total':total,'coupon':coupon}
    else:
        context={'ord':ord,'addr':addr,'ord_data':ord_data,'total':total}
    return render(request,"user/order_details.html",context)

def sample(request):
    return render(request,"user/sample.html")


def cancel_order(request,order_id):
    order=Order.objects.get(id=order_id)
    order.status="Cancelled"
    if(order.pay_method=="Razor Pay"):
        refund=order.tot_amount
        get_wallet=Wallet.objects.get(user_id=request.user)
        get_wallet.balance=get_wallet.balance+refund
        get_wallet.save()
    order.save()
    return redirect(orders)

def return_order(request,order_id):
    order=Order.objects.get(id=order_id)
    order.status="Return"
    if(order.pay_method=="Razor Pay"):
        refund=order.tot_amount
        get_wallet=Wallet.objects.get(user_id=request.user)
        get_wallet.balance=get_wallet.balance+refund
        get_wallet.save()
    order.save()
    return redirect(orders)
    
def notification(request):
    notifications=Notification.objects.filter(user=request.user)
    return render(request,"user/notification.html",{'notifications':notifications})

def address(request):
    user_address=Address.objects.filter(user=request.user,remove_address=True)
    return render(request,"user/address.html",{'user_address':user_address})

def edit_address(request,address_id):
    user_address=Address.objects.get(id=address_id)
    if request.method == "POST":
        user_address.remove_address=False
        user_address.save()
        name=request.POST['name'] 
        addr=request.POST['addr'] 
        pin=request.POST['pin'] 
        ph_no=request.POST['ph_no'] 
        area=request.POST['area'] 
        city=request.POST['city'] 
        state=request.POST['state'] 
        type=request.POST['type']
        new_add=Address(user=request.user,name=name,addr=addr,pin=pin,ph_no=ph_no,area=area,city=city,state=state,type=type)
        new_add.save()
        return redirect(address)
    return render(request,"user/view_address.html",{'user_address':user_address})

def add_wishlist(request,variant_id):
    if request.user.is_authenticated:
        product=Wishlist(item_id=variant_id,user=request.user)
        product.save()
        return redirect(view_wishlist)
    else:
        return redirect(user_login)
    
def view_wishlist(request):
    if request.user.is_authenticated:
        wishlist_items=Wishlist.objects.filter(user=request.user).select_related('item') 
        return render(request,"user/wishlist.html",{'wishlist_items':wishlist_items})    
    else:
        return redirect(user_login)
    
def remove_wishlist(request,wishlist_id):
    wishlist_item=Wishlist.objects.get(id=wishlist_id)
    wishlist_item.delete()
    return redirect(view_wishlist)
    
def profile(request):
    if request.user.is_authenticated:
        user_details=User.objects.get(username=request.user)
        balance=Wallet.objects.get(user=user_details.id)
        context={'user_details':user_details,'balance':balance}
        return render(request,"user/profile.html",context)
    else:
        return redirect(user_login)

def invoice(request,or_id):
    ord=Order.objects.get(id=or_id).new_order.all().select_related('item')
    ord_data=Order.objects.get(id=or_id)
    addr=Address.objects.get(id=ord_data.del_add_id)
    total=0
    for o in ord:
        total+=o.sub_tot
    if(ord_data.coupon_apply):
        coupon=Coupon.objects.get(id=ord_data.coupon_apply_id)
        context={'ord':ord,'addr':addr,'ord_data':ord_data,'total':total,'coupon':coupon}
    else:
        context={'ord':ord,'addr':addr,'ord_data':ord_data,'total':total}
    html_string = get_template('user/invoice.html').render(context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Create an HTTP response with the PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_.pdf"'

    return response

def apply_coupon(request):
    cur_user=request.user
    crt=Cart.objects.filter(user=cur_user,val=False).select_related('prd_id')
    tot=0
    for p in crt:
        tot=tot+p.prd_var.cur_price * p.qty
    context={'crt':crt,'tot':tot}
    if request.method == "POST":
        code=request.POST['code']
        if Coupon.objects.filter(code=code).exists():
            request.session['coupon']=code
            print(request.session['coupon'])
            return render(request,"user/cart1.html",context)
        else:
            messages.info(request,"Invalid Coupon")
            return render(request,"user/cart1.html",context)
    
          
    