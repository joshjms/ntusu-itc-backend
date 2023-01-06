from django.contrib import admin
from sso.models import User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'display_name', 'email',
                    'is_active', 'is_staff')


admin.site.register(User, CustomUserAdmin)
