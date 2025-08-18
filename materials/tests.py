from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from materials.models import Course, Lesson, Subscription
from users.models import User

class LessonCRUDAndSubscriptionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", password="pass1234")
        self.moderator = User.objects.create_user(email="moderator@example.com", password="pass1234", is_staff=True)
        self.other_user = User.objects.create_user(email="other@example.com", password="pass1234")

        # Обычно модераторы принадлежат к группе "Модераторы".
        # Если требуется, можно создать и добавить группу, но для тестов достаточно проверить поведение NotModerator.

        # Создаем курс и урок, принадлежавшие владельцу
        self.course = Course.objects.create(
            course_name="Test Course",
            description="Описание тестового курса",
            owner=self.owner,
        )
        self.lesson = Lesson.objects.create(
            lesson_name="Test Lesson",
            description="Описание тестового урока",
            course=self.course,
            owner=self.owner,
        )

        self.lesson_list_url = reverse("lesson-list-create")  # /lessons/
        self.lesson_detail_url = reverse(
            "lesson-detail", kwargs={"pk": self.lesson.pk}
        )  # /lessons/<id>/
        self.subscription_url = reverse("subscriptions")  # /subscriptions/

    def test_lesson_create_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "lesson_name": "New Lesson",
            "description": "Описание нового урока",
            "course": self.course.id,
        }
        response = self.client.post(self.lesson_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_forbidden_for_moderator(self):
        # Модератор не должен иметь права создавать уроки (NotModerator не проходит)
        self.client.force_authenticate(user=self.moderator)
        data = {
            "lesson_name": "New Lesson",
            "description": "Описание нового урока",
            "course": self.course.id,
        }
        response = self.client.post(self.lesson_list_url, data, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

    def test_lesson_create_forbidden_for_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "lesson_name": "New Lesson",
            "description": "Описание нового урока",
            "course": self.course.id,
        }
        response = self.client.post(self.lesson_list_url, data, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
        )

    def test_lesson_update_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {"lesson_name": "Updated Title"}
        response = self.client.patch(self.lesson_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["lesson_name"], data["lesson_name"])


class SubscriptionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.course = Course.objects.create(course_name="Test Course", description="Описание курса", owner=self.user)
        self.url = reverse("subscriptions")  # /subscriptions/

    def test_subscribe_to_course(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Подписка создана")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_requires_authentication(self):
        response = self.client.post(
            self.url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_without_course_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course_id не указан", response.data.get("error", ""))


