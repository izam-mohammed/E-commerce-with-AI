from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    cat_name=models.CharField(max_length=20)
    cat_desc=models.CharField(max_length=50)
    cat_img=models.ImageField(upload_to='images')
    cat_status=models.BooleanField(null=True,blank=True)
    
      
class Brand(models.Model):
    brd_name=models.CharField(max_length=20)
    brd_desc=models.CharField(max_length=50)
    brd_img=models.ImageField(upload_to='images')
    brd_status=models.BooleanField(null=True,blank=True)

    
   
class Product(models.Model):
    prd_name=models.CharField(max_length=20)
    brd_id=models.ForeignKey(Brand, on_delete=models.CASCADE)
    cat_id=models.ForeignKey(Category, on_delete=models.CASCADE)
    desc=models.CharField(max_length=50)
    warr=models.CharField(max_length=30,null=True,blank=True)
    
    
class PrdVariation(models.Model):
    prd_id=models.ForeignKey(Product, on_delete=models.CASCADE)
    color=models.CharField(max_length=20)
    stock=models.IntegerField()
    cur_price=models.FloatField()
    max_price=models.FloatField()
    p1_img=models.FileField(upload_to='images')
    p2_img=models.FileField(upload_to='images')
    p3_img=models.FileField(upload_to='images')
    prd_status=models.BooleanField()
    
class Cart(models.Model):
    prd_id=models.ForeignKey(Product, on_delete=models.CASCADE)
    prd_var=models.ForeignKey(PrdVariation, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    qty=models.IntegerField()
    val=models.BooleanField(default=False)
    
class Address(models.Model):
    CHOICES = [
        ('Home', 'Home'),
        ('Office', 'Office'),
    ]
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=20)
    addr=models.CharField(max_length=50)
    pin=models.CharField(max_length=10)
    ph_no=models.CharField(max_length=10)
    area=models.CharField(max_length=20)
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=20)
    type=models.CharField(max_length=10,choices=CHOICES,)
    remove_address=models.BooleanField(default=True)
    
class OrderItem(models.Model):
    item=models.ForeignKey(PrdVariation, on_delete=models.CASCADE)
    qty=models.IntegerField()
    sub_tot=models.FloatField()
    status = models.CharField(max_length=20, default="Order Placed")
    
class Coupon(models.Model):
    code=models.CharField(max_length=20)
    value=models.CharField(max_length=5)
    status=models.BooleanField(default=True)
    
class Order(models.Model):
    new_order=models.ManyToManyField(OrderItem)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    tot_amount=models.FloatField()
    del_add=models.ForeignKey(Address, on_delete=models.CASCADE)
    razor_pay_id = models.CharField(blank=True, null=True, max_length=100)
    status=models.CharField(max_length=20, default="Pending")
    created_at=models.DateField(default=timezone.now)
    pay_method=models.CharField(max_length=20,blank=True, null=True)
    return_date=models.DateField(blank=True, null=True)
    coupon_apply=models.ForeignKey(Coupon, on_delete=models.CASCADE,blank=True, null=True)
    
    
class Banner(models.Model):
    name=models.CharField(max_length=20)
    ban1_img=models.FileField(upload_to='images')
    ban2_img=models.FileField(upload_to='images',blank=True, null=True)
    ban3_img=models.FileField(upload_to='images',blank=True, null=True)
    ban4_img=models.FileField(upload_to='images',blank=True, null=True)
    status=models.BooleanField(default=False)
    
class Wallet(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    balance=models.FloatField()
    
class Notification(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateField(default=timezone.now)
    description=models.CharField(max_length=50)

class Wishlist(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    item=models.ForeignKey(PrdVariation, on_delete=models.CASCADE)
    
