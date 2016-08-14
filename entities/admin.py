from django.contrib import admin
from .models import Entity, UserEntity
# Register your models here.


def make_activated(modeladmin, request, queryset):
    queryset.update(status='A')
make_activated.short_description = "Mark selected entities as Activated"

def make_pending(modeladmin, request, queryset):
    queryset.update(status='P')
make_pending.short_description = "Mark selected entities as Pending"

def make_rejected(modeladmin, request, queryset):
    queryset.update(status='R')
make_rejected.short_description = "Mark selected entities as Rejected"


class EntitiesListAdmin(admin.ModelAdmin):
    list_display = [x.name for x in Entity._meta.local_fields]
    actions = [make_activated,make_pending,make_rejected]
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

