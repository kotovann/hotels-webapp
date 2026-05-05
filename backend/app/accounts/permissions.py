from rest_framework.permissions import BasePermission


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class GuestOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_guest


class ModeratorOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_moderator


class SelfOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
