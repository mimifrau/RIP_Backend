import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


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

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_taxs():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    codes = Code.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_tax(status, codes, owner, moderators)

    add_tax(1, codes, users[0], moderators)
    add_tax(2, codes, users[0], moderators)

    print("Заявки добавлены")


def add_tax(status, codes, owner, moderators):
    tax = Tax.objects.create()
    tax.status = status

    if tax.status in [3, 4]:
        tax.moderator = random.choice(moderators)
        tax.date_complete = random_date()
        tax.date_formation = tax.date_complete - random_timedelta()
        tax.date_created = tax.date_formation - random_timedelta()
    else:
        tax.date_formation = random_date()
        tax.date_created = tax.date_formation - random_timedelta()

    tax.owner = owner
    tax.moderator = random.choice(moderators)

    tax.date = random_date()

    for code in random.sample(list(codes), 3):
        item = CodeTax(
            tax=tax,
            code=code,
            value=random.randint(1000, 3000)
        )
        item.save()

    tax.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_codes()
        add_taxs()
