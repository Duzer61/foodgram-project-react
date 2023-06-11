from rest_framework.permissions import BasePermission


class IsSubscribeOnly(BasePermission):
    """Разрешает удаление только для действий с подписками."""
    def has_permission(self, request, view):
        return view.action == 'subscribe'
