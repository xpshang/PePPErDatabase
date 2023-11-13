from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group,AbstractUser
# Register your models here.
from .models import CustomUser, SuperUser


class CustomUserAdmin(UserAdmin):
    list_display = (
    'username', 'email','last_login','date_joined','is_superuser')
    fieldsets = (
        (None, {'fields': ('username','email', 'password','is_superuser')}),

    )
    add_fieldsets = (
        (None, {
            'fields': ('username','email', 'password1', 'password2','is_superuser'),
        }),
    )
    def get_queryset(self, request):

        qs = super(UserAdmin, self).get_queryset(request)
        qs=qs.filter(is_superuser=0)
        return qs.all()

class SuperUserAdmin(UserAdmin):
    list_display = (
    'username', 'email','last_login','date_joined','is_superuser')
    fieldsets = (
        (None, {'fields': ('username','email', 'password','is_superuser')}),

    )
    add_fieldsets = (
        (None, {
            'fields': ('username','email', 'password1', 'password2','is_superuser'),
        }),
    )
    def get_queryset(self, request):

        qs = super(UserAdmin, self).get_queryset(request)
        qs=qs.filter(is_superuser=1)
        return qs.all()


admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(SuperUser,SuperUserAdmin)
admin.site.unregister(Group)