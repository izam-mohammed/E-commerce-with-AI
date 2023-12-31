from django.urls import path
from hps.views import *

urlpatterns = [
    path('', index,name='index'),
    path('register',register,name='register'),
    path('user_login',user_login,name='user_login'),
    path('user_logout',user_logout,name='user_logout'),
    path('view_prod<int:pid>',view_prod,name='view_prod'),
    path('brand_wise<int:bid>',brand_wise,name='brand_wise'),
    path('cat_wise<int:cid>',cat_wise,name='cat_wise'),
    path('search_result',search_result,name='search_result'),
    path('cart',cart,name='cart'),
    path('add_add',add_add,name='add_add'),
    path('checkout<int:ad_id>',checkout,name='checkout'),
    path('view_add',view_add,name='view_add'),
    path('add_cart<int:pid>',add_cart,name='add_cart'),
    path('rem_cart<int:cid>',rem_cart,name='rem_cart'),
    path('inc_qty/<int:item_id>/',inc_qty,name='inc_qty'),
    path('dec_qty/<int:item_id>/',dec_qty,name='dec_qty'),
    path('create_order<int:ad_id>',create_order,name='create_order'),
    path('r_paid<int:or_id>',r_paid,name='r_paid'),
    path('cod_paid<int:or_id>',cod_paid,name='cod_paid'),
    path('orders',orders,name='orders'),
    path('ord_details<int:or_id>',ord_details,name='ord_details'),
    path('sample',sample,name='sample'),
    path('cancel_order<int:order_id>',cancel_order,name='cancel_order'),
    path('return_order<int:order_id>',return_order,name='return_order'),
    path('notification',notification,name='notification'),
    path('address',address,name='address'),
    path('edit_address<int:address_id>',edit_address,name='edit_address'),
    path('add_wishlist<int:variant_id>',add_wishlist,name='add_wishlist'),
    path('view_wishlist',view_wishlist,name='view_wishlist'),
    path('remove_wishlist<int:wishlist_id>',remove_wishlist,name='remove_wishlist'),
    path('profile',profile,name='profile'),
    path('invoice<int:or_id>',invoice,name='invoice'),
    path('apply_coupon',apply_coupon,name='apply_coupon'),
]



