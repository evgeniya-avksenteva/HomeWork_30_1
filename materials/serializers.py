from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
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

    class Meta:
        model = Course
        fields = ["id", "course_name", "description", "lessons", "lessons_count"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()
