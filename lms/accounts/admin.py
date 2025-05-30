from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_teacher', 'is_student', 'is_staff']
    
    # Remove Groups and User permissions from the admin add/edit user forms
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('User Type', {'fields': ('is_teacher', 'is_student')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    # For user creation form in admin, similarly remove groups and permissions fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_teacher', 'is_student', 'is_staff', 'is_superuser'),
        }),
    )

    # Optionally, you can disable groups and user_permissions from being displayed at all
    filter_horizontal = ()  # remove the groups and permissions multi-select widgets

admin.site.register(CustomUser, CustomUserAdmin)
