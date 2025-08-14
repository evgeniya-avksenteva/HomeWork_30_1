from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnlyOrModerator(BasePermission):
    def has_permission(self, request, view):
        # Запрещаем создание/удаление модераторам на уровне представления (для коллекций)
        # Пример: модератор не должен создавать (POST) или удалять (DELETE) записи.
        if request.user.groups.filter(name="Модераторы").exists():
            # Разрешаем только чтение и редактирование (PUT/PATCH) для объектов,
            # но запрещаем создание/удаление на уровне view (пользователь не владеет конкретным объектом).
            if view.action in ["create", "destroy"]:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name="Модераторы").exists():
            if request.method in SAFE_METHODS:
                return True
            if request.method in ["PUT", "PATCH"]:
                return True
            return False

        if request.method in SAFE_METHODS:
            return True

        return obj.owner == request.user
