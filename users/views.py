from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, generics, permissions
from users.models import Payment
from users.filters import PaymentFilter



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ['email']

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    # Для сортировки по дате оплаты через параметр ordering
    ordering_fields = ['payment_date']


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
