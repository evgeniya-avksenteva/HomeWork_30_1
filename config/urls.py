from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def index(request):
    return HttpResponse("Добро пожаловать!")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("materials/", include("materials.urls")),
    # Включение маршрутов из users/urls.py
    path('api/', include(('users.urls', 'users'), namespace='users')),
    # JWT токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]