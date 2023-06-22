from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import User
from .models import Follow


class CustomUserAdmin(UserAdmin):
    list_filter = (
        'email', 'username', 'is_staff', 'is_superuser', 'is_active', 'groups'
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user__username', 'following__username')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
