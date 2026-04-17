from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group as BaseGroup
from app.accounts.models import User, Group, GroupPriority


class GroupPriorityInline(admin.TabularInline):
    model = GroupPriority
    min_num = 1
    extra = 1
    validate_min = True
    can_delete = False


admin.site.unregister(BaseGroup)
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupPriorityInline,)
    list_display = ('name', 'priority')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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
            'fields': ('groups', 'user_permissions'),
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
            'fields': ('groups',),
        }),
    )

    @admin.display(description='ФИО', ordering=('last_name', 'middle_name', 'first_name'))
    def full_name(self, obj):
        '''
        Возвращает полное имя пользователя
        '''
        return obj.full_name

    @admin.display(description='Основная роль')
    def role(self, obj):
        return obj.role

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups', 'groups__group_priority')
