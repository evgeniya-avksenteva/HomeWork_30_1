from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from materials.models import Course, Lesson

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Укажите почту"
    )

    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите свой аватар",
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
    )
    city = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите название города",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


# class Payment(models.Model):
#     PAYMENT_METHOD_CHOICES = [
#         ("cash", "Наличные"),
#         ("bank_transfer", "Перевод на счет"),
#     ]
#
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
#     lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
#
#     def __str__(self):
#         return f"{self.user} - {self.amount} on {self.payment_date}"


class Payment(models.Model):
    amount = models.PositiveIntegerField(
        verbose_name="Сумма оплаты",
        help_text="Введите сумму оплаты",
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Id сессии",
        help_text="Введите id сессии",
    )
    link = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Оплаченный курс",
        help_text="Укажите курс, за который произведена оплата",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "В ожидании"),
            ("paid", "Оплачено"),
            ("failed", "Не удалось"),
        ],
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"
