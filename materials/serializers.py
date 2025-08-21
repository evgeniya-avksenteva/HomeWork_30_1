from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_allowed_url


class LessonSerializer(ModelSerializer):
    video_url = serializers.URLField(
        validators=[validate_allowed_url], required=False, allow_blank=True
    )
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "lesson_name"]


class CourseSerializer(ModelSerializer):
    lessons = LessonShortSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "course_name",
            "description",
            "lessons",
            "lessons_count",
            "is_subscribed",
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
