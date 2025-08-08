from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def index(request):
    return HttpResponse("Добро пожаловать!")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("materials/", include("materials.urls")),
    path('api/', include(('users.urls', 'users'), namespace='users')),
]
