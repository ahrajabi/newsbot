from django.contrib import admin

# Register your models here.
from .models import UserProfile, UserAlert, UserNews, UserNewsList, UserSettings, MessageFromUser

def username(obj):
    return obj.user.username

def email(obj):
    return obj.user.email

def joined(obj):
    return obj.user.date_joined

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'activated', username, email, joined, 'first_name', 'last_name', 'last_chat')

admin.site.register(UserProfile,UserProfileAdmin)


class UserAlertListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserAlert._meta.local_fields]
    list_filter = (
        ('is_sent'),
    )
admin.site.register(UserAlert,UserAlertListAdmin)


@admin.register(UserNews)
class UserNewsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserNews._meta.local_fields]


@admin.register(UserNewsList)
class UserNewsListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserNewsList._meta.local_fields]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserSettings._meta.local_fields]


@admin.register(MessageFromUser)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in MessageFromUser._meta.local_fields]

