from rest_framework import generics, viewsets

from materials.models import Course, Lesson
from materials.permissions import IsOwnerOrReadOnlyOrModerator
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrReadOnlyOrModerator]

    def get_queryset(self):
        user = self.request.user
        is_moderator = bool(
            user.is_authenticated and user.groups.filter(name="Модераторы").exists()
        )
        if is_moderator:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrReadOnlyOrModerator]

    def get_queryset(self):
        user = self.request.user
        is_moderator = bool(
            user.is_authenticated and user.groups.filter(name="Модераторы").exists()
        )
        if is_moderator:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrReadOnlyOrModerator]

    def get_queryset(self):
        user = self.request.user
        is_moderator = bool(
            user.is_authenticated and user.groups.filter(name="Модераторы").exists()
        )
        if is_moderator:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)
