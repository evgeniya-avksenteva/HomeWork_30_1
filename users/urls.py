from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import PaymentViewSet, UserRegistrationView, UserViewSet

app_name = "users"
router = DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
]
