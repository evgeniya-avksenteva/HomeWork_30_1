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


class IsOwnerProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем авторизованным (если нужна такая логика). Можно убрать, если нужна только аутентификация.
        if request.method in SAFE_METHODS:
            return True
        # Редактирование/удаление — только своему профилю
        return obj.id == getattr(request.user, "id", None)
