import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    sort_by_date = django_filters.OrderingFilter(
        fields=('payment_date',),
        label='Сортировка по дате оплаты'
    )
    course_id = django_filters.NumberFilter(field_name='course__id')
    lesson_id = django_filters.NumberFilter(field_name='lesson__id')
    payment_method = django_filters.CharFilter(field_name='payment_method')

    class Meta:
        model = Payment
        fields = ['course_id', 'lesson_id', 'payment_method']
