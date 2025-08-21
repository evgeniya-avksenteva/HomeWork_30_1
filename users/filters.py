import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    sort_by_date = django_filters.OrderingFilter(
        fields=("created_at",), label="Сортировка по дате оплаты"
    )
    course_id = django_filters.NumberFilter(field_name="course__id", label="ID курса")
    lesson_id = django_filters.NumberFilter(field_name="lesson__id")
    payment_method = django_filters.CharFilter(field_name="payment_method")

    class Meta:
        model = Payment
        fields = []
