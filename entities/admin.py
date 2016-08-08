from django.contrib import admin
from .models import Entity, UserEntity
# Register your models here.

class EntitiesListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Entity._meta.local_fields]
    list_filter = (
        ('status'),
    )
admin.site.register(Entity,EntitiesListAdmin)

class UserEntitiesListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in UserEntity._meta.local_fields]
    list_filter = (
        ('status'),
    )
admin.site.register(UserEntity,UserEntitiesListAdmin)

