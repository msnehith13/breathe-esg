from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Organization', {'fields': ('org',)}),
    )
    list_display = ['username', 'email', 'org', 'is_superuser']