from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User
from users.models import Payment


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'payment_date',
            'course',
            'lesson',
            'amount',
            'payment_method',
        ]
        read_only_fields = ['payment_date']
