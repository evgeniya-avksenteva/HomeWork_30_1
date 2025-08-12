from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Модераторы").exists()
        )


class IsNotModerator(BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # чтение разрешено всем авторизованным пользователям,
        # изменение — только владельцу или модератору.
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.user == request.user
            or request.user.groups.filter(name="Модераторы").exists()
        )
