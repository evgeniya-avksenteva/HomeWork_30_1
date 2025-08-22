from rest_framework import generics, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from materials.models import Course, Lesson, Subscription
from materials.paginators import StandardResultsSetPagination
from materials.permissions import IsOwner, NotModerator
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionCreateSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action == "create":
            # любой авторизованный, но не модератор
            permission_classes = [IsAuthenticated, NotModerator]
        else:
            # update, partial_update, destroy
            permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        # Добавить защиту от анонимности
        if not self.request.user or not self.request.user.is_authenticated:
            return qs  # или вернуть публичные курсы, если нужно
        if not self.request.user.groups.filter(name="Модераторы").exists():
            qs = qs.filter(owner=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        action = getattr(self, "action", None)
        if action in ["list", "retrieve"] or self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif action == "create" or self.request.method == "POST":
            permission_classes = [IsAuthenticated, NotModerator]
        else:
            permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user or not self.request.user.is_authenticated:
            return qs.none()
        if not self.request.user.groups.filter(name="Модераторы").exists():
            qs = qs.filter(owner=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        course_id = request.data.get("course")
        if not course_id:
            return Response({"error": "course не указан"}, status=400)
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден"}, status=404)
        if course.owner != user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        action = getattr(self, "action", None)
        if action == "retrieve" or self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        else:  # update/partial_update/destroy
            permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user or not self.request.user.is_authenticated:
            return qs.none()
        if not self.request.user.groups.filter(name="Модераторы").exists():
            qs = qs.filter(owner=self.request.user)
        return qs


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Подписаться/отписаться на курс",
        request_body=SubscriptionCreateSerializer,
        responses={
            200: openapi.Response(
                description="Результат подписки",
                examples={
                    "application/json": {"message": "Подписка создана"}
                },
            ),
            400: openapi.Response(description="Ошибка ввода"),
            401: openapi.Response(description="НеАвторизован"),
            403: openapi.Response(description="Доступ запрещён"),
        },
    )

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course")

        if not course_id:
            return Response({"error": "course не указан"}, status=400)

        course = get_object_or_404(Course, id=course_id)
        subs_qs = Subscription.objects.filter(user=user, course=course)

        if subs_qs.exists():
            subs_qs.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка создана"

        return Response({"message": message})
