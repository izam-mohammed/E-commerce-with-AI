from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from hps.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.template.loader import get_template
from weasyprint import HTML

# Create your views here.


def adm_index(request):
    """
    View for the admin dashboard.

    Displays various statistics like order count, total revenue, active customers, and monthly order counts.
    """
    if request.user.is_superuser:
        item_count = OrderItem.objects.filter(status="Order Placed").count()
        total_revenue = (
            OrderItem.objects.filter(status="Order Placed").aggregate(
                order_sum=Sum("sub_tot")
            )["order_sum"]
            or 0
        )
        active_customers = User.objects.filter(is_active=True).count()
        order_counts = (
            Order.objects.annotate(month=ExtractMonth("created_at"))
            .annotate(year=ExtractYear("created_at"))
            .values("year", "month")
            .annotate(count=Count("id"))
        )
        month_counts = [0] * 12
        for entry in order_counts:
            month = entry["month"]
            count = entry["count"]
            month_counts[month - 1] = count
        context = {
            "month_counts": month_counts,
            "item_count": item_count,
            "total_revenue": total_revenue,
            "active_customers": active_customers,
        }
        return render(request, "adm/adm_index.html", context)
    else:
        return redirect(adm_login)


def adm_login(request):
    """
    View for admin login.

    Authenticates the admin and redirects to the admin dashboard if successful.
    """
    if request.method == "POST":
        uname = request.POST.get("username")
        upass = request.POST.get("password")
        myuser = authenticate(username=uname, password=upass)
        if myuser is not None and myuser.is_superuser:
            login(request, myuser)
            # messages.success(request,"Login Success")
            return redirect(adm_index)
        else:
            messages.error(request, "Invalid Credentails")
            return redirect("/adm_login")
    return render(request, "adm/adm_login.html")


def view_cat(request):
    """
    View for displaying all categories.

    Shows a list of all categories for admin users.
    """
    if request.user.is_superuser:
        cat = Category.objects.all().order_by("-id")
        context = {"cat": cat}
        return render(request, "adm/view_cat.html", context)
    else:
        return redirect(adm_login)


def view_brd(request):
    """
    View for displaying all brands.

    Shows a list of all brands for admin users.
    """
    if request.user.is_superuser:
        brd = Brand.objects.all().order_by("-id")
        context = {"brd": brd}
        return render(request, "adm/view_brd.html", context)
    else:
        return redirect(adm_login)


def view_prd(request):
    """
    View for displaying all products.

    Shows a list of all products for admin users.
    """
    if request.user.is_superuser:
        prd = Product.objects.all().select_related("brd_id", "cat_id").order_by("-id")
        context = {"prd": prd}
        return render(request, "adm/view_prd.html", context)
    else:
        return redirect(adm_login)


def add_cat(request):
    """
    Adds a new category if the user is a superuser.

    Checks for existing categories, and if none, saves the new category and redirects to view_cat.
    """
    if request.user.is_superuser:
        if request.method == "POST":
            cname = request.POST["name"]
            cdesc = request.POST["desc"]
            cimg = request.FILES["img"]
            if Category.objects.filter(cat_name__iexact=cname).exists():
                messages.info(request, "Category already exists.")
            else:
                cat = Category(
                    cat_name=cname, cat_desc=cdesc, cat_img=cimg, cat_status="True"
                )
                cat.save()
                return redirect(view_cat)
        return render(request, "adm/add_cat.html")
    else:
        return redirect(adm_login)


def add_brd(request):
    """
    Adds a new brand if the user is a superuser.

    Checks for existing brands, and if none, saves the new brand and redirects to view_brd.
    """
    if request.user.is_superuser:
        if request.method == "POST":
            bname = request.POST["name"]
            bdesc = request.POST["desc"]
            bimg = request.FILES["img"]
            if Brand.objects.filter(brd_name__iexact=bname).exists():
                messages.info(request, "Brand already exists.")
            else:
                brd = Brand(
                    brd_name=bname, brd_desc=bdesc, brd_img=bimg, brd_status="True"
                )
                brd.save()
                return redirect(view_brd)
        return render(request, "adm/add_brd.html")
    else:
        return redirect(adm_login)


def adm_logout(request):
    """
    Logs out the admin user and redirects to adm_login.
    """
    logout(request)
    # messages.info(request,"Logout Success")
    return redirect(adm_login)


def up_cat(request, cid):
    """
    Updates a category based on the provided category ID.

    Validates and saves the updated category details and redirects to view_cat.
    """
    cat = Category.objects.get(id=cid)
    if request.method == "POST":
        cname = request.POST["name"]
        cimg = request.FILES.get("img")
        cat1 = Category.objects.filter(cat_name__iexact=cname).exclude(id=cid)
        if cat1.exists():
            messages.info(request, "Category already exists.")
        elif cimg is None:
            cat.cat_name = request.POST["name"]
            cat.cat_desc = request.POST["desc"]
            cat.cat_status = request.POST["status"]
            cat.save()
            return redirect(view_cat)
        else:
            cat.cat_name = request.POST["name"]
            cat.cat_desc = request.POST["desc"]
            cat.cat_img = request.FILES["img"]
            cat.cat_status = request.POST["status"]
            cat.save()
            return redirect(view_cat)
    return render(request, "adm/up_cat.html", {"cat": cat})


def up_brd(request, bid):
    """
    Updates a brand based on the provided brand ID.

    Validates and saves the updated brand details and redirects to view_cat.
    """
    brd = Brand.objects.get(id=bid)
    if request.method == "POST":
        bname = request.POST["name"]
        bimg = request.FILES.get("img")
        brd1 = Brand.objects.filter(brd_name__iexact=bname).exclude(id=bid)
        if brd1.exists():
            messages.info(request, "Brand already exists.")
        elif bimg is None:
            brd.brd_name = request.POST["name"]
            brd.brd_desc = request.POST["desc"]
            brd.brd_status = request.POST["status"]
            brd.save()
            return redirect(view_brd)
        else:
            brd.brd_name = request.POST["name"]
            brd.brd_desc = request.POST["desc"]
            brd.brd_img = request.FILES["img"]
            brd.brd_status = request.POST["status"]
            brd.save()
            return redirect(view_cat)
    return render(request, "adm/up_brd.html", {"brd": brd})


def add_prd(request):
    """
    Adds a new product if the user is a superuser.

    Validates and saves the new product details and redirects to view_prd.
    """
    cat = Category.objects.filter(cat_status=True)
    brd = Brand.objects.filter(brd_status=True)
    context = {"cat": cat, "brd": brd}
    if request.user.is_superuser:
        if request.method == "POST":
            pname = request.POST["name"]
            categ = request.POST["categ"]
            brand = request.POST["brand"]
            pdesc = request.POST["desc"]
            war = request.POST["war"]
            if Product.objects.filter(prd_name__iexact=pname).exists():
                messages.info(request, "Product already exists.")
            else:
                prd = Product(
                    prd_name=pname,
                    cat_id_id=categ,
                    brd_id_id=brand,
                    desc=pdesc,
                    warr=war,
                )
                prd.save()
                return redirect(view_prd)
        return render(request, "adm/add_prd.html", context)
    else:
        return redirect(adm_login)


def up_prd(request, pid):
    """
    Updates a product based on the provided product ID.

    Validates and saves the updated product details and redirects to view_prd.
    """
    prd = Product.objects.filter(id=pid).select_related("brd_id", "cat_id")[0]
    cat = Category.objects.filter(cat_status=True)
    brd = Brand.objects.filter(brd_status=True)
    context = {"cat": cat, "brd": brd, "prd": prd}
    if request.method == "POST":
        pname = request.POST["name"]
        prd1 = Product.objects.filter(prd_name__iexact=pname).exclude(id=pid)
        if prd1.exists():
            messages.info(request, "Product already exists.")
        else:
            prd.prd_name = request.POST["name"]
            prd.brd_id_id = request.POST["brand"]
            prd.cat_id_id = request.POST["categ"]
            prd.warr = request.POST["war"]
            prd.desc = request.POST["desc"]
            prd.save()
            return redirect(view_prd)
    return render(request, "adm/up_prd.html", context)


def variant(request):
    """
    Displays all product variations for superuser.

    Retrieves and displays all product variations.
    """
    if request.user.is_superuser:
        prd = PrdVariation.objects.all().select_related("prd_id").order_by("-id")
        context = {"prd": prd}
        return render(request, "adm/variation.html", context)
    else:
        return redirect(adm_login)


def add_var(request):
    """
    Adds a new product variation if the user is a superuser.

    Validates and saves the new product variation details and redirects to variant.
    """
    prd = Product.objects.all()
    context = {"prd": prd}
    if request.user.is_superuser:
        if request.method == "POST":
            prdt = request.POST["prdt"]
            color = request.POST["color"]
            stock = request.POST["stock"]
            cprice = request.POST["cprice"]
            mprice = request.POST["mprice"]
            img1 = request.FILES["img1"]
            img2 = request.FILES["img2"]
            img3 = request.FILES["img3"]
            if PrdVariation.objects.filter(color__iexact=color, prd_id=prdt).exists():
                messages.info(request, "Variant already exists.")
            else:
                prd = PrdVariation(
                    prd_id_id=prdt,
                    color=color,
                    stock=stock,
                    cur_price=cprice,
                    max_price=mprice,
                    p1_img=img1,
                    p2_img=img2,
                    p3_img=img3,
                    prd_status=True,
                )
                prd.save()
                return redirect(variant)
        return render(request, "adm/add_var.html", context)
    else:
        return redirect(adm_login)


def up_var(request, pid):
    """
    Updates a product variation based on the provided variation ID.

    Validates and saves the updated variation details and redirects to variant.
    """
    prdt = Product.objects.all()
    prd = PrdVariation.objects.filter(id=pid).select_related("prd_id")[0]
    print(prd)
    context = {"prd": prd, "prdt": prdt}
    if request.user.is_superuser:
        if request.method == "POST":
            prd.prd_id_id = request.POST["prdt"]
            prd.color = request.POST["color"]
            prd.stock = request.POST["stock"]
            prd.cur_price = request.POST["cprice"]
            prd.max_price = request.POST["mprice"]
            prd.prd_status = request.POST["status"]
            img1 = request.FILES.get("img1")
            img2 = request.FILES.get("img2")
            img3 = request.FILES.get("img3")
            if img1:
                prd.p1_img = img1
            if img2:
                prd.p2_img = img2
            if img3:
                prd.p3_img = img3
            prd1 = PrdVariation.objects.filter(
                color__iexact=prd.color, prd_id_id=prd.prd_id_id
            ).exclude(id=pid)
            if prd1.exists():
                messages.info(request, "Variant already exists.")
            else:
                prd.save()
                return redirect(variant)
        return render(request, "adm/up_var.html", context)
    else:
        return redirect(adm_login)


def reports(request):
    """
    Displays all order reports.

    Retrieves and displays all order reports for the superuser.
    """
    all_report = Order.objects.all().select_related("user").order_by("-id")
    context = {"all_report": all_report}
    return render(request, "adm/reports.html", context)


def date_report(request):
    """
    Displays order reports for a specific date.

    Retrieves and displays order reports based on the selected date.
    """
    if request.method == "POST":
        selected_date = request.POST["selected_date"]
        all_report = Order.objects.filter(created_at=selected_date).order_by("-id")
        context = {"all_report": all_report, "selected_date": selected_date}
        return render(request, "adm/date_report.html", context)
    return render(request, "adm/date_report.html")


def week_report(request):
    """
    Displays order reports for a specific week.

    Retrieves and displays order reports based on the selected week.
    """
    if request.method == "POST":
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        all_report = Order.objects.filter(
            created_at__range=(start_date, end_date)
        ).order_by("-id")
        context = {
            "all_report": all_report,
            "start_date": start_date,
            "end_date": end_date,
        }
        return render(request, "adm/week_report.html", context)
    return render(request, "adm/week_report.html")


def year_report(request):
    """
    Displays order reports for a specific year.

    Retrieves and displays order reports based on the selected year.
    """
    if request.method == "POST":
        selected_year = request.POST["selected_year"]
        all_report = Order.objects.filter(created_at__year=selected_year).order_by(
            "-id"
        )
        context = {"all_report": all_report, "selected_year": selected_year}
        return render(request, "adm/year_report.html", context)
    return render(request, "adm/year_report.html")


def veiw_report(request, order_id):
    """
    View for displaying detailed information about a specific order.

    Allows admin users to view and update the status of an order.
    """
    order_details = Order.objects.get(id=order_id)
    order_items = Order.objects.get(id=order_id).new_order.all().select_related("item")
    total = 0
    addrress = Address.objects.get(id=order_details.del_add_id)
    context = {
        "order_details": order_details,
        "order_items": order_items,
        "addrress": addrress,
    }
    if request.method == "POST":
        order_details.status = request.POST["status"]
        r_date = request.POST["return_date"]
        if r_date:
            order_details.return_date = r_date
        order_details.save()
        return redirect(reports)
    return render(request, "adm/view_report.html", context)


def add_ban(request):
    """
    View for adding a new banner.

    Allows admin users to add a new banner with multiple images.
    """
    if request.method == "POST":
        banner_name = request.POST["name"]
        image_1 = request.FILES["img1"]
        image_2 = request.FILES["img2"]
        image_3 = request.FILES["img3"]
        image_4 = request.FILES["img4"]
        new_banner = Banner(
            name=banner_name,
            ban1_img=image_1,
            ban2_img=image_2,
            ban3_img=image_3,
            ban4_img=image_4,
            status=False,
        )
        new_banner.save()
        return redirect(banner)
    return render(request, "adm/add_ban.html")


def banner(request):
    """
    View for displaying all banners.

    Shows a list of all banners for admin users.
    """
    ban = Banner.objects.all().order_by("-id")
    return render(request, "adm/banner.html", {"ban": ban})


def up_ban(request, ban_id):
    """
    View for updating a banner.

    Allows admin users to update the details and images of a specific banner.
    """
    ban = Banner.objects.get(id=ban_id)
    if request.method == "POST":
        banner1_image = request.FILES.get("img1")
        banner2_image = request.FILES.get("img2")
        banner3_image = request.FILES.get("img3")
        banner4_image = request.FILES.get("img4")
        if banner1_image:
            ban.ban1_img = banner1_image
        if banner2_image:
            ban.ban2_img = banner2_image
        if banner3_image:
            ban.ban3_img = banner3_image
        if banner4_image:
            ban.ban4_img = banner4_image
        ban.name = request.POST["name"]
        ban.save()
        return redirect(banner)
    return render(request, "adm/up_ban.html", {"ban": ban})


# def ban_mgmt(request):
#     ban=Banner.objects.all()
#     return render(request,"adm/ban_mgmt.html",{'ban':ban})


def active_banner(request, banner_id):
    """
    View for activating a specific banner.

    Sets the selected banner as active and deactivates all other banners.
    """
    ban = Banner.objects.all()
    ban.update(status=False)
    ban = Banner.objects.get(id=banner_id)
    ban.status = True
    ban.save()
    return redirect(banner)


def add_coupon(request):
    """
    View for adding a new coupon.

    Allows admin users to add a new coupon code with a specific discount value.
    """
    if request.method == "POST":
        code = request.POST["code"]
        value = request.POST["value"]
        if Coupon.objects.filter(code__iexact=code).exists():
            messages.error(request, "Coupon already exists")
        else:
            new_coupon = Coupon(code=code, value=value)
            new_coupon.save()
            return redirect(view_coupon)
    return render(request, "adm/add_coupon.html")


def view_coupon(request):
    """
    View for displaying all coupons.

    Shows a list of all active and inactive coupons for admin users.
    """
    coupons = Coupon.objects.all().order_by("-id")
    return render(request, "adm/view_coupon.html", {"coupons": coupons})


def edit_coupon(request, coupon_id):
    """
    View for editing the status of a coupon.

    Allows admin users to activate or deactivate a specific coupon.
    """
    coupons = Coupon.objects.get(id=coupon_id)
    if request.method == "POST":
        coupons.status = request.POST["status"]
        coupons.save()
        return redirect(view_coupon)
    return render(request, "adm/edit_coupon.html", {"coupons": coupons})


def export_report(request):
    """
    View for exporting the complete order report as a PDF.
    """
    orders = Order.objects.all().select_related("user").order_by("-id")
    context = {"orders": orders}
    html_string = get_template("adm/export_report.html").render(context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Create an HTTP response with the PDF
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="report_.pdf"'

    return response


def export_date(request, selected_date):
    """
    View for exporting the order report for a specific date as a PDF.
    """
    orders = Order.objects.filter(created_at=selected_date).order_by("-id")
    string = "Reports of date " + selected_date
    context = {"orders": orders, "string": string}
    html_string = get_template("adm/export_report.html").render(context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Create an HTTP response with the PDF
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="report_.pdf"'

    return response


def export_week(request, start_date, end_date):
    """
    View for exporting the order report for a specific week as a PDF.
    """
    print(start_date)
    print(end_date)
    print(end_date)
    orders = Order.objects.filter(created_at__range=(start_date, end_date)).order_by(
        "-id"
    )
    string = "Reports from " + start_date + " to " + end_date
    context = {"orders": orders, "string": string}
    html_string = get_template("adm/export_report.html").render(context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Create an HTTP response with the PDF
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="report_.pdf"'

    return response


def export_year(request, selected_year):
    """
    View for exporting the order report for a specific year as a PDF.
    """
    orders = Order.objects.filter(created_at__year=selected_year).order_by("-id")
    string = "Reports of year " + selected_year
    context = {"orders": orders, "string": string}
    html_string = get_template("adm/export_report.html").render(context)

    # Convert HTML to PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Create an HTTP response with the PDF
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="report_.pdf"'

    return response
