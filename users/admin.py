from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import path

@admin.action(description='Set custom default password for selected users')
def set_custom_password(modeladmin, request, queryset):
    # Check if the "Apply Password" button was clicked in the intermediate form
    if 'apply' in request.POST:
        password = request.POST.get('custom_password')
        if password:
            count = 0
            for user in queryset:
                user.set_password(password)
                user.must_change_password = False 
                user.save()
                count += 1
            modeladmin.message_user(request, f"Successfully set a new custom password for {count} users.", messages.SUCCESS)
            return HttpResponseRedirect(request.get_full_path())
        else:
            modeladmin.message_user(request, "Password cannot be empty. No changes made.", messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

    # If 'apply' is not in POST, show the intermediate page
    context = {
        'title': 'Set Custom Default Password',
        'users': queryset,
    }
    return render(request, 'admin/set_custom_password.html', context)

from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'role', 'course', 'is_staff')
    list_filter = ('role', 'course', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    compressed_fields = True
    warn_unsaved_form = True
    actions = [set_custom_password]
    
    # Ensure custom fields are visible in the admin
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'course')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'course', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Force student password to be their username
        if obj.role == 'student':
            obj.set_password(obj.username)
            obj.must_change_password = False
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('bulk-password-reset/', self.admin_site.admin_view(self.bulk_password_reset_view), name='bulk_password_reset'),
        ]
        return my_urls + urls

    def bulk_password_reset_view(self, request):
        if request.method == 'POST':
            target_group = request.POST.get('target_group')
            target_user_id = request.POST.get('target_user')
            new_password = request.POST.get('new_password')
            
            if not new_password:
                messages.error(request, "Password cannot be empty.")
                return HttpResponseRedirect(request.path)
                
            users_to_update = []
            if target_user_id:
                try:
                    user = User.objects.get(id=target_user_id)
                    users_to_update.append(user)
                except User.DoesNotExist:
                    messages.error(request, "Selected user does not exist.")
                    return HttpResponseRedirect(request.path)
            elif target_group:
                if target_group == 'all_lecturers':
                    users_to_update = list(User.objects.filter(role='lecturer'))
                elif target_group == 'all_students':
                    users_to_update = list(User.objects.filter(role='student'))
                elif target_group == 'all_users':
                    users_to_update = list(User.objects.all())
                    
            if not users_to_update:
                messages.warning(request, "No users selected to update.")
                return HttpResponseRedirect(request.path)
                
            count = 0
            for user in users_to_update:
                user.set_password(new_password)
                user.must_change_password = False
                user.save()
                count += 1
                
            messages.success(request, f"Successfully reset passwords for {count} user(s).")
            return HttpResponseRedirect(request.path)
            
        context = dict(
            self.admin_site.each_context(request),
            title="Bulk Password Reset",
            users=User.objects.all().order_by('username'),
        )
        return render(request, "admin/bulk_password_reset.html", context)

