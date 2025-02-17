from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Code, Tax, CodeTax


def index(request):
    code_name = request.GET.get("code_name", "")
    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    draft_tax = get_draft_tax()

    context = {
        "code_name": code_name,
        "codes": codes
    }

    if draft_tax:
        context["codes_count"] = len(draft_tax.get_codes())
        context["draft_tax"] = draft_tax

    return render(request, "codes_page.html", context)


def add_code_to_draft_tax(request, code_id):
    code_name = request.POST.get("code_name")
    redirect_url = f"/?code_name={code_name}" if code_name else "/"

    code = Code.objects.get(pk=code_id)

    draft_tax = get_draft_tax()

    if draft_tax is None:
        draft_tax = Tax.objects.create()
        draft_tax.owner = get_current_user()
        draft_tax.date_created = timezone.now()
        draft_tax.save()

    if CodeTax.objects.filter(tax=draft_tax, code=code).exists():
        return redirect(redirect_url)

    item = CodeTax(
        tax=draft_tax,
        code=code
    )
    item.save()

    return redirect(redirect_url)


def code_details(request, code_id):
    context = {
        "code": Code.objects.get(id=code_id)
    }

    return render(request, "code_page.html", context)


def delete_tax(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE taxs SET status=5 WHERE id = %s", [tax_id])

    return redirect("/")


def tax(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return render(request, "404.html")

    tax = Tax.objects.get(id=tax_id)
    if tax.status == 5:
        return render(request, "404.html")

    context = {
        "tax": tax,
    }

    return render(request, "tax_page.html", context)


def get_draft_tax():
    return Tax.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()