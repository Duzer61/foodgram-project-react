from rest_framework import permissions


class IsSubscribeOnly(permissions.BasePermission):
    """Разрешает удаление только для действий с подписками."""
    def has_permission(self, request, view):
        return view.action == 'subscribe'


class IsAuthorOrAuthenticatedOrReadOnly(permissions.BasePermission):
    """Разрешает просмотр всем, пост - авторизованным,
        изменение и удаление только автору."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
