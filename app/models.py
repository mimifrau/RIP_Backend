from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Code(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Налог", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    decryption = models.CharField(blank=True)

    def get_image(self):
        if self.image:
            return self.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

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
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Сотрудник", null=True, related_name='moderator')

    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Списание №" + str(self.pk)

    def get_codes(self):
        return [
            setattr(item.code, "value", item.value) or item.code
            for item in CodeTax.objects.filter(tax=self)
        ]

    class Meta:
        verbose_name = "Списание"
        verbose_name_plural = "Списания"
        ordering = ('-date_formation',)
        db_table = "taxs"


class CodeTax(models.Model):
    code = models.ForeignKey(Code, on_delete=models.DO_NOTHING, blank=True, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "code_tax"
        constraints = [
            models.UniqueConstraint(fields=['code', 'tax'], name="code_tax_constraint")
        ]
