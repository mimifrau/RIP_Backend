from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Code(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Налог")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    decryption = models.CharField(verbose_name="Расшифровка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Код"
        verbose_name_plural = "Коды"
        db_table = "codes"


class Tax(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Бухгалтер", related_name='moderator', blank=True,  null=True)

    date = models.DateField(blank=True, null=True)
    charge = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Списание №" + str(self.pk)

    class Meta:
        verbose_name = "Списание"
        verbose_name_plural = "Списания"
        db_table = "taxs"
        ordering = ('-date_formation', )


class CodeTax(models.Model):
    code = models.ForeignKey(Code, on_delete=models.DO_NOTHING, blank=True, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.DO_NOTHING, blank=True, null=True)
    summ = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "code_tax"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['code', 'tax'], name="code_tax_constraint")
        ]
