import stripe
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import Payment
from users.services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
)

from .models import User
from .permissions import IsOwnerProfile
from .serializers import (
    CreatePaymentSerializer,
    PaymentSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["email"]

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [IsOwnerProfile]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class PaymentAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer  # Для вывода (только id)

    def perform_create(self, serializer):
        data = self.request.data
        input_serializer = CreatePaymentSerializer(data=data)
        input_serializer.is_valid(raise_exception=True)

        price_decimal = input_serializer.validated_data["price"]
        course_id = input_serializer.validated_data["course_id"]

        # Получаем курс
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise serializers.ValidationError("Курс не найден.")

        amount_cents = int(price_decimal * 100)

        product_name = course.course_name if course else "Course Payment"
        product_description = getattr(course, "description", "")

        # Создаем Stripe продукт и цену
        product = create_stripe_product(
            name=product_name,
            description=product_description,
        )
        price_obj = create_stripe_price(product.id, amount=amount_cents)

        success_url = f"http://127.0.0.1:8000/materials/courses/{course.id}/"
        cancel_url = "https://yourdomain.com/materials/payment-cancelled/"

        session = create_stripe_checkout_session(
            price_id=price_obj.id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        # Создаем платеж в базе
        payment = serializer.save(
            amount=amount_cents,
            session_id=session.id,
            link=session.url,
            user=self.request.user,
            course=course,
            status="pending",
        )

        # Запоминаем ответ (только id)
        self.response_data = {"id": payment.id, "payment_url": session.url}

    def create(self, request, *args, **kwargs):
        self.response_data = {}
        self.perform_create(self.get_serializer())
        return Response(self.response_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Создание платежа: формирование Stripe продукта/цены/сессии",
        request_body=CreatePaymentSerializer,
        responses={
            201: openapi.Response(
                description="Создан платеж",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка валидации"),
        },
    )
    def create(self, request, *args, **kwargs):
        self.response_data = {}
        response = super().create(request, *args, **kwargs)
        return Response(self.response_data, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение статуса платежа по payment_id",
        responses={
            200: openapi.Response(
                description="Статус платежа",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                        "amount_total": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "currency": openapi.Schema(type=openapi.TYPE_STRING),
                        "customer_details": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "payment_intent": openapi.Schema(type=openapi.TYPE_STRING),
                        "session_id": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка запроса"),
            404: openapi.Response(description="Платеж не найден"),
        },
    )
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Платеж не найден."}, status=status.HTTP_404_NOT_FOUND
            )

        session_id = payment.session_id
        if not session_id:
            return Response(
                {"error": "ID сессии отсутствует."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer_details": session.customer_details,
                "payment_intent": session.payment_intent,
                "session_id": session.id,
            }
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
