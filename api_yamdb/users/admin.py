from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка админки для модели User."""

    list_display = ('pk', 'username', 'email', 'first_name', 'last_name', 'role', 'bio')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'role')
    list_filter = ('role',)
    list_editable = ('role',)
    empty_value_display = 'Значение отсутствует'
    list_per_page = 10

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        ('Роли', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'bio')}),
        ('Роли', {'fields': ('role',)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
