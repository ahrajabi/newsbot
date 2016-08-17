from django.contrib import admin

# Register your models here.
from .models import UserProfile, UserAlert

def username(obj):
    return obj.user.username

def email(obj):
    return obj.user.email

def joined(obj):
    return obj.user.date_joined

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('telegram_id',username, email, joined, 'first_name','last_name','last_chat')

admin.site.register(UserProfile,UserProfileAdmin)


class UserAlertListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserAlert._meta.local_fields]
    list_filter = (
        ('is_sent'),
    )
admin.site.register(UserAlert,UserAlertListAdmin)
