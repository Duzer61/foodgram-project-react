from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from recipes.models import User


class CustomUserAdmin(UserAdmin):
    list_filter = (
        'email', 'username', 'is_staff', 'is_superuser', 'is_active', 'groups'
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
