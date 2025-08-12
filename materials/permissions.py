from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает только владельцу объекта редактировать его,
    остальные могут только читать.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы всем авторизованным пользователям
        if request.method in SAFE_METHODS:
            return True

        return obj.owner == request.user
