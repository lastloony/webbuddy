from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form to generate temporary password on user creation
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'fio_name', 'email', 'project')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password fields not required for admin creation
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate temporary password if not provided
        if not self.cleaned_data.get('password1'):
            temp_password = get_random_string(12)
            user.set_password(temp_password)
            # Store temp password for display (in real app, send via email)
            user._temp_password = temp_password
        user.first_login = True
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with password reset functionality
    """
    add_form = CustomUserCreationForm
    list_display = ('username', 'fio_name', 'email', 'role', 'project', 'first_login', 'is_active', 'is_staff')
    list_filter = ('role', 'project', 'first_login', 'is_active', 'is_staff')
    search_fields = ('username', 'fio_name', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('fio_name', 'email', 'project', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'first_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'fio_name', 'email', 'project', 'role', 'password1', 'password2'),
        }),
    )

    actions = ['reset_password_to_temp']

    def reset_password_to_temp(self, request, queryset):
        """
        Admin action to reset user password to temporary
        """
        for user in queryset:
            temp_password = get_random_string(12)
            user.set_password(temp_password)
            user.first_login = True
            user.save()
            # In production, send email with temp password
            self.message_user(request, f'Password for {user.username} reset to: {temp_password}')

    reset_password_to_temp.short_description = "Reset password to temporary"