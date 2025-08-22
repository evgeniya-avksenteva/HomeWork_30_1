import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.serializers import PaymentCreateSerializer
from users.models import Payment
from users.services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
)

from .models import User
from .permissions import IsOwnerProfile
from .serializers import PaymentSerializer, UserRegistrationSerializer, UserSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        """Получаем данные платежа из serializer.validated_data"""
        course = serializer.validated_data.get("course")
        amount = serializer.validated_data.get("amount") * 100

        product_name = course.course_name if course else "Course Payment"
        product_description = getattr(course, "description", "")

        product = create_stripe_product(
            name=product_name,
            description=product_description if product_description else "",
        )
        price = create_stripe_price(product.id, amount=amount)

        course_id = course.id if course else None
        success_url = (
            f"http://127.0.0.1:8000/materials/{course_id}/"
            if course_id
            else "http://127.0.0.1:8000/materials/"
        )
        cancel_url = "https://yourdomain.com/materials/payment-cancelled/"
        session = create_stripe_checkout_session(
            price_id=price.id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment = serializer.save(
            amount=serializer.validated_data.get("amount"),
            session_id=session.id,
            link=session.url,
            user=self.request.user,
            course=course,
        )

        self.response_data = {"payment_id": payment.id, "checkout_url": session.url}

    @swagger_auto_schema(
        operation_description="Создание платежа: формирование Stripe продукта/цены/сессии",
        request_body=PaymentCreateSerializer,
        responses={
            201: openapi.Response(
                description="Создан платеж",
                PaymentSerializerschema=PaymentSerializer,
                examples={
                    "application/json": {
                        "id": 123,
                        "user": 1,
                        "created_at": "2025-08-21T12:34:56Z",
                        "course": 2,
                        "amount": 1500,
                        "session_id": "sess_ABC",
                        "link": "https://checkout.stripe.com/sess_ABC",
                        "status": "pending",
                    }
                },
            )
        },
    )


    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(self.response_data, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение статуса платежа по session_id",
        manual_parameters=[
            openapi.Parameter(
                "session_id",
                openapi.IN_QUERY,
                description="ID сессии Stripe",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Статус платежа",
                examples={
                    "application/json": {
                        "id": "sess_1ABCDEFG",
                        "payment_status": "paid",
                        "amount_total": 10000,
                        "currency": "usd",
                        "customer_details": {"email": "user@example.com"},
                        "payment_intent": "pi_1ABCDEFG",
                    }
                },
            ),
            400: openapi.Response(description="Ошибка запроса"),
            404: openapi.Response(description="Сессия не найдена"),
        },
    )


    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "session_id не указан"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": session.id,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer_details": session.customer_details,
                "payment_intent": session.payment_intent,
            }
        )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
