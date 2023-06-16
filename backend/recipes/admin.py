from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Favourites, Follow, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, User)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('amount', 'recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favourite_count')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('name', 'author__username', 'tags__name')
    readonly_fields = ('in_favourite_count', )
    inlines = (IngredientInline,)

    def in_favourite_count(self, recipe):
        """Подсчитывает сколь раз рецепт добавлен в избранное."""
        return recipe.favourite.count()

    in_favourite_count.short_description = 'В избранном'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user__username', 'following__username')


class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')


class CustomUserAdmin(UserAdmin):
    list_filter = (
        'email', 'username', 'is_staff', 'is_superuser', 'is_active', 'groups'
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
