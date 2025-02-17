import random

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_tax():
    return Tax.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_codes(request):
    code_name = request.GET.get("code_name", "")

    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    serializer = CodesSerializer(codes, many=True)
    
    draft_tax = get_draft_tax()

    resp = {
        "codes": serializer.data,
        "codes_count": CodeTax.objects.filter(tax=draft_tax).count() if draft_tax else None,
        "draft_tax": draft_tax.pk if draft_tax else None
    }

    return Response(resp)


@api_view(["GET"])
def get_code_by_id(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    serializer = CodeSerializer(code)

    return Response(serializer.data)


@api_view(["PUT"])
def update_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    serializer = CodeSerializer(code, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_code(request):
    serializer = CodeSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Code.objects.create(**serializer.validated_data)

    codes = Code.objects.filter(status=1)
    serializer = CodeSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    code.status = 2
    code.save()

    codes = Code.objects.filter(status=1)
    serializer = CodeSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_code_to_tax(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    draft_tax = get_draft_tax()

    if draft_tax is None:
        draft_tax = Tax.objects.create()
        draft_tax.owner = get_user()
        draft_tax.date_created = timezone.now()
        draft_tax.save()

    if CodeTax.objects.filter(tax=draft_tax, code=code).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = CodeTax.objects.create()
    item.tax = draft_tax
    item.code = code
    item.save()

    serializer = TaxSerializer(draft_tax)
    return Response(serializer.data["codes"])


@api_view(["POST"])
def update_code_image(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    image = request.data.get("image")
    if image is not None:
        code.image = image
        code.save()

    serializer = CodeSerializer(code)

    return Response(serializer.data)


@api_view(["GET"])
def search_taxs(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    taxs = Tax.objects.exclude(status__in=[1, 5])

    if status > 0:
        taxs = taxs.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        taxs = taxs.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        taxs = taxs.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = TaxsSerializer(taxs, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_tax_by_id(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)
    serializer = TaxSerializer(tax, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_tax(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)
    serializer = TaxSerializer(tax, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)

    if tax.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tax.status = 2
    tax.date_formation = timezone.now()
    tax.save()

    serializer = TaxSerializer(tax, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tax = Tax.objects.get(pk=tax_id)

    if tax.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        for item in CodeTax.objects.filter(tax=tax):
            item.summ = random.randint(1, 10)
            item.save()

    tax.date_complete = timezone.now()
    tax.status = request_status
    tax.moderator = get_moderator()
    tax.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_tax(request, tax_id):
    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)

    if tax.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tax.status = 5
    tax.save()

    serializer = TaxSerializer(tax, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_code_from_tax(request, tax_id, code_id):
    if not CodeTax.objects.filter(tax_id=tax_id, code_id=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeTax.objects.get(tax_id=tax_id, code_id=code_id)
    item.delete()

    items = CodeTax.objects.filter(tax_id=tax_id)
    data = [CodeItemSerializer(item.code, context={"summ": item.summ}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_code_in_tax(request, tax_id, code_id):
    if not CodeTax.objects.filter(code_id=code_id, tax_id=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeTax.objects.get(code_id=code_id, tax_id=tax_id)

    serializer = CodeTaxSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)