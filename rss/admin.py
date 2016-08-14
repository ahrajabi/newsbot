from django.contrib import admin
from .models import RssFeeds, News, BaseNews


@admin.register(RssFeeds)
class RssAdmin(admin.ModelAdmin):
    list_display = ('fa_name', 'name', 'url', 'main_rss', 'last_modified', 'selector', 'summary_selector')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('basenews_ptr_id', 'summary')

@admin.register(BaseNews)
class BaseNewsAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'published_date', 'rss_id')
