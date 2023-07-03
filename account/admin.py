from django.contrib import admin
from .models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

admin.site.site_header = 'EXCOIN'


# Пользователи
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_html_avatar', 'get_full_name', 'email',)
    list_display_links = list_display
    list_filter = ('is_superuser', 'is_staff', 'is_verified', 'date_joined',)
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'date_joined')
    readonly_fields = ('balance', 'date_joined',)
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'second_name',
        'balance',
        'phone',
        'passport',
        'avatar',
        'is_superuser',
        'is_staff',
        'is_verified',
        'is_active',
        'date_joined',
        'last_login',
        'user_permissions',
        'groups'
    )

    def get_html_avatar(self, object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")

    def get_full_name(self, object):
        return mark_safe(f"{object.first_name} {object.last_name}")

    get_html_avatar.short_description = _('Avatar')
    get_full_name.short_description = 'Full name'
