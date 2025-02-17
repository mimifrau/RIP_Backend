from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *
from ...services.qr_generate import generate_tax_qr


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_codes():
    Code.objects.create(
        name="1010",
        description="Дивиденды — это часть прибыли, которой компания делится с инвесторами, владеющими их акциями. Некоторые компании выплачивают дивиденды от 1 до 12 раз в год — периодичность и размер выплат указываются в дивидендной политике конкретной компании.",
        decryption="Дивиденды",
        image="1.png"
    )

    Code.objects.create(
        name="1220",
        description="Под страховыми взносами понимаются обязательные платежи на обязательное пенсионное страхование, обязательное социальное страхование на случай временной нетрудоспособности и в связи с материнством, на обязательное медицинское страхование.",
        decryption="Суммы страховых взносов",
        image="2.png"
    )

    Code.objects.create(
        name="1537",
        description="Процент по займу – это сумма, которую клиент платит за пользование средствами, полученными в долг.",
        decryption="Доходы в виде процентов по займу",
        image="3.png"
    )

    Code.objects.create(
        name="1549",
        description="Ценная бумага — это финансовое средство, дающее заимодавцу (инвестору) обеспеченное законом право получать в будущем определенный доход в установленном порядке.",
        decryption="Доходы, полученные по операциям с ценными бумагами",
        image="4.png"
    )

    Code.objects.create(
        name="2014",
        description="По правилам Трудового кодекса, в случае увольнения работодатель должен компенсировать сотруднику временную потерю заработка.",
        decryption="Сумма выплаты в виде выходного пособия",
        image="5.png"
    )

    Code.objects.create(
        name="2017",
        description="Полевое довольствие – это компенсационная выплата, которая связана с разъездным характером работы или работой в полевых условиях",
        decryption="Суточные или полевое довольствие работникам",
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_taxs():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    codes = Code.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_tax(status, codes, owner, moderators)

    add_tax(1, codes, users[0], moderators)
    add_tax(2, codes, users[0], moderators)
    add_tax(3, codes, users[0], moderators)
    add_tax(4, codes, users[0], moderators)
    add_tax(5, codes, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_tax(status, codes, users[0], moderators)


def add_tax(status, codes, owner, moderators):
    tax = Tax.objects.create()
    tax.status = status

    if status in [3, 4]:
        tax.moderator = random.choice(moderators)
        tax.date_complete = random_date()
        tax.date_formation = tax.date_complete - random_timedelta()
        tax.date_created = tax.date_formation - random_timedelta()
    else:
        tax.date_formation = random_date()
        tax.date_created = tax.date_formation - random_timedelta()

    tax.name = "Морозов Илья Александрович"

    tax.owner = owner

    items = []
    for code in random.sample(list(codes), 3):
        item = CodeTax(
            tax=tax,
            code=code,
            paid=random.randint(10, 100) * 100
        )
        item.save()
        items.append(item)

    if status == 3:
        tax.summ = 100 * random.randint(1, 100)
        tax.qr = generate_tax_qr(tax, items, timezone.now())

    tax.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_codes()
        add_taxs()
