from django.contrib import admin
from .models import theaccount, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
# Register your models here.

class theaccountAdmin(UserAdmin): #this method would also harse the passwords
    list_display = ('id', 'email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = () #when using custom user model and you want to use list display you have to specify from line 11 to 9 else you would have an error
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(theaccount, theaccountAdmin)

admin.site.register(UserProfile, UserProfileAdmin)
