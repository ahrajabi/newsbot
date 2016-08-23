from django.contrib import admin

from .models import RssFeeds, News, BaseNews, ImageUrls


def related_obj_id(obj):
    return obj.id


@admin.register(RssFeeds)
class RssAdmin(admin.ModelAdmin):
    list_display = ('fa_name', 'name', 'url', 'main_rss', 'last_modified', 'selector', 'summary_selector')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('base_news', 'pic_number', 'summary', 'id')


@admin.register(BaseNews)
class BaseNewsAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'published_date', 'complete_news', 'rss_id', 'id', 'save_to_elastic')


@admin.register(ImageUrls)
class ImageUrlsAdmin(admin.ModelAdmin):
    list_display = (related_obj_id, 'img_url')
