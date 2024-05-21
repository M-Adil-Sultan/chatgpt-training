from django.contrib import admin
from .models import Chat
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html

class UserAdmin(BaseUserAdmin):
    change_list_template = 'admin/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('activate/<int:user_id>/', self.admin_site.admin_view(self.activate_user), name='activate_user'),
            path('deactivate/<int:user_id>/', self.admin_site.admin_view(self.deactivate_user), name='deactivate_user'),
        ]
        return custom_urls + urls

    def activate_user(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        self.message_user(request, f'{user.username} was activated successfully.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def deactivate_user(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        self.message_user(request, f'{user.username} was deactivated successfully.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def action_buttons(self, obj):
        if obj.is_active:
            return format_html(
                '<a class="button" href="{}">Deactivate</a>',
                f'deactivate/{obj.pk}/'
            )
        else:
            return format_html(
                '<a class="button" href="{}">Activate</a>',
                f'activate/{obj.pk}/'
            )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    list_display = ('date_joined', 'username', 'email', 'is_active', 'action_buttons')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)



admin.site.register(Chat)