from django.contrib import admin

from .models import RssFeeds, News, BaseNews, ImageUrls


def related_obj_id(obj):
    return obj.id


@admin.register(RssFeeds)
class RssAdmin(admin.ModelAdmin):
    list_display = [x.name for x in RssFeeds._meta.local_fields]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in News._meta.local_fields]


@admin.register(BaseNews)
class BaseNewsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in BaseNews._meta.local_fields]
    list_filter = (
        ('rss_id'),
    )

@admin.register(ImageUrls)
class ImageUrlsAdmin(admin.ModelAdmin):
    list_display = (related_obj_id, 'img_url')
