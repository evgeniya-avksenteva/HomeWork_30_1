from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class NotModerator(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return not request.user.groups.filter(name="Модераторы").exists()
