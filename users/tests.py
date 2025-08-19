from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserPermissionsUnittest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="ownerpass",
            phone="111",
            city="Москва",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="otherpass",
            phone="222",
            city="Санкт-Петербург",
        )
        # Путь к деталям пользователя
        self.user_detail_url = lambda user_id: reverse(
            "users:users-detail", kwargs={"pk": user_id}
        )
        self.login_url = "/api/token/"
        # Получаем токены для каждого пользователя
        self.owner_token = self._obtain_token(self.owner.email, "ownerpass")
        self.other_token = self._obtain_token(self.other.email, "otherpass")

    def _obtain_token(self, email, password):
        resp = self.client.post(
            self.login_url, {"email": email, "password": password}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        return resp.data.get("access")

    def _auth_header(self, token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_owner_can_update_profile(self):
        url = self.user_detail_url(self.owner.pk)
        data = {"phone": "+7 999 888 77 66"}
        resp = self.client.patch(
            url, data, format="json", **self._auth_header(self.owner_token)
        )
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])

        # проверить, что данные обновились
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.phone, data["phone"])

    def test_non_owner_cannot_update_profile(self):
        url = self.user_detail_url(self.owner.pk)
        data = {"phone": "+7 111 222 333"}
        resp = self.client.patch(
            url, data, format="json", **self._auth_header(self.other_token)
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_profile(self):
        url = self.user_detail_url(self.owner.pk)
        resp = self.client.delete(url, **self._auth_header(self.owner_token))
        self.assertIn(
            resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )
        # Убедиться, что пользователь удален
        self.assertFalse(User.objects.filter(pk=self.owner.pk).exists())

    def test_non_owner_cannot_delete_profile(self):
        url = self.user_detail_url(self.owner.pk)
        resp = self.client.delete(url, **self._auth_header(self.other_token))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_detail_requires_no_auth_or_is_allowed(self):
        # GET без авторизации
        url = self.user_detail_url(self.owner.pk)
        resp = self.client.get(url, format="json")
        # Из вашего кода: SAFE_METHODS разрешены, поэтому 200 ожидаем
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
