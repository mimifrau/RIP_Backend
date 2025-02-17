import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_tax(request):
    user = identity_user(request)

    if user is None:
        return None

    tax = Tax.objects.filter(owner=user).filter(status=1).first()

    return tax


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'code_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_codes(request):
    code_name = request.GET.get("code_name", "")

    codes = Code.objects.filter(status=1)

    if code_name:
        codes = codes.filter(name__icontains=code_name)

    serializer = CodesSerializer(codes, many=True)

    draft_tax = get_draft_tax(request)

    resp = {
        "codes": serializer.data,
        "codes_count": CodeTax.objects.filter(tax=draft_tax).count() if draft_tax else None,
        "draft_tax_id": draft_tax.pk if draft_tax else None
    }

    return Response(resp)


@api_view(["GET"])
def get_code_by_id(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    serializer = CodeSerializer(code)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=CodeSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    serializer = CodeSerializer(code, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=CodeAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_code(request):
    serializer = CodeAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Code.objects.create(**serializer.validated_data)

    codes = Code.objects.filter(status=1)
    serializer = CodesSerializer(codes, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_code(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)
    code.status = 2
    code.save()

    code = Code.objects.filter(status=1)
    serializer = CodeSerializer(code, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_code_to_tax(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    draft_tax = get_draft_tax(request)

    if draft_tax is None:
        draft_tax = Tax.objects.create()
        draft_tax.date_created = timezone.now()
        draft_tax.owner = identity_user(request)
        draft_tax.save()

    if CodeTax.objects.filter(tax=draft_tax, code=code).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = CodeTax.objects.create()
    item.tax = draft_tax
    item.code = code
    item.save()

    serializer = TaxSerializer(draft_tax)
    return Response(serializer.data["codes"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_code_image(request, code_id):
    if not Code.objects.filter(pk=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = Code.objects.get(pk=code_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    code.image = image
    code.save()

    serializer = CodeSerializer(code)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_taxs(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    taxs = Tax.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        taxs = taxs.filter(owner=user)

    if status_id > 0:
        taxs = taxs.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        taxs = taxs.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        taxs = taxs.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = TaxsSerializer(taxs, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tax_by_id(request, tax_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)

    if not user.is_superuser and tax.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TaxSerializer(tax)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=TaxSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_tax(request, tax_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)
    serializer = TaxSerializer(tax, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, tax_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)

    if tax.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tax.status = 2
    tax.date_formation = timezone.now()
    tax.save()

    serializer = TaxSerializer(tax)

    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
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
        tax.summ = 100 * random.randint(1, 100)

    tax.status = request_status
    tax.date_complete = timezone.now()
    tax.moderator = identity_user(request)
    tax.save()

    serializer = TaxSerializer(tax)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_tax(request, tax_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tax = Tax.objects.get(pk=tax_id)

    if tax.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tax.status = 5
    tax.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_code_from_tax(request, tax_id, code_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CodeTax.objects.filter(tax_id=tax_id, code_id=code_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeTax.objects.get(tax_id=tax_id, code_id=code_id)
    item.delete()

    tax = Tax.objects.get(pk=tax_id)

    serializer = TaxSerializer(tax)
    codes = serializer.data["codes"]

    return Response(codes)


@swagger_auto_schema(method='PUT', request_body=CodeTaxSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_code_in_tax(request, tax_id, code_id):
    user = identity_user(request)

    if not Tax.objects.filter(pk=tax_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CodeTax.objects.filter(code_id=code_id, tax_id=tax_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CodeTax.objects.get(code_id=code_id, tax_id=tax_id)

    serializer = CodeTaxSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
