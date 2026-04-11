from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'role')
    list_per_page = 30
    list_filter = ('date_of_birth', 'groups', 'is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('last_name', 'middle_name', 'first_name', 'email')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone_number'),
        }),
        ('Учётные данные', {
            'fields': ('email', 'password'),
        }),
        ('Группы и роли', {
            'fields': ('groups', 'primary_group', 'user_permissions'),
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    add_fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone_number'),
        }),
        ('Учётные данные', {
            'fields': ('email', 'password'),
        }),
        ('Группы и роли', {
            'fields': ('groups', 'primary_group'),
        }),
    )

    @admin.display(description='Полное имя', ordering=('last_name', 'middle_name', 'first_name'))
    def full_name(self, obj):
        '''
        Возвращает полное имя пользователя
        '''
        return obj.full_name

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')
