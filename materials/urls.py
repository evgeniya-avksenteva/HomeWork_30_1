from django.urls import include, path
from rest_framework.routers import DefaultRouter

from materials.views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
    SubscriptionAPIView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")


urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
]
