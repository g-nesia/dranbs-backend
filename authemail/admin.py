from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from authemail.forms import EmailUserCreationForm, EmailUserChangeForm
from authemail.models import SignupCode, PasswordResetCode, EmailChangeCode


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'ipaddr', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'code', 'ipaddr')


class SignupCodeInline(admin.TabularInline):
    model = SignupCode
    fieldsets = (
        (None, {
            'fields': ('code', 'ipaddr', 'created_at')
        }),
    )
    readonly_fields = ('code', 'ipaddr', 'created_at')


class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'code')


class PasswordResetCodeInline(admin.TabularInline):
    model = PasswordResetCode
    fieldsets = (
        (None, {
            'fields': ('code', 'created_at')
        }),
    )
    readonly_fields = ('code', 'created_at')


class EmailChangeCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'email', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'code', 'email')


class EmailChangeCodeInline(admin.TabularInline):
    model = EmailChangeCode
    fieldsets = (
        (None, {
            'fields': ('code', 'email', 'created_at')
        }),
    )
    readonly_fields = ('code', 'email', 'created_at')


class EmailUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    inlines = [SignupCodeInline, EmailChangeCodeInline, PasswordResetCodeInline]
    list_display = ('id', 'email', 'username', 'is_verified', 'first_name', 'last_name',
                    'is_staff')
    search_fields = ('first_name', 'last_name', 'email', 'username',)
    ordering = ('email',)


admin.site.register(get_user_model(), EmailUserAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(PasswordResetCode, PasswordResetCodeAdmin)
admin.site.register(EmailChangeCode, EmailChangeCodeAdmin)
