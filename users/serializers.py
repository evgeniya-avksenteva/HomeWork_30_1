from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import Payment

from .models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id"]
        read_only_fields = ["id"]


class CreatePaymentSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    course_id = serializers.IntegerField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "phone", "city", "avatar"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
