from rest_framework import serializers

from materials.models import Course, Lesson

from rest_framework.serializers import ModelSerializer


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
