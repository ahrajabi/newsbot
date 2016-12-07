from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import RssFeeds, News, BaseNews, ImageUrls, NewsLike, CategoryCode, NewsAgency, TelegramPost, BadNews


def related_obj_id(obj):
    return obj.id


@admin.register(RssFeeds)
class RssAdmin(admin.ModelAdmin):
    list_display = [x.name for x in RssFeeds._meta.local_fields]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in News._meta.local_fields]
    list_display.remove('body')
    search_fields = ('body', 'summary')

@admin.register(BadNews)
class NewsAdmin(admin.ModelAdmin):
    list_display = [x.name for x in BadNews._meta.fields]
    search_fields = ('body', 'summary')


@admin.register(BaseNews)
class BaseNewsAdmin(admin.ModelAdmin):
    def get_all_rss(self, obj):
        return "\n".join([p.news_agency.fa_name +" " + p.category for p in obj.all_rss.all()])

    list_display = [x.name for x in BaseNews._meta.local_fields]
    list_display.append('get_all_rss')



@admin.register(ImageUrls)
class ImageUrlsAdmin(admin.ModelAdmin):
    list_display = (related_obj_id, 'img_url')


@admin.register(NewsLike)
class NewsLikeAdmin(admin.ModelAdmin):
    list_display = [x.name for x in NewsLike._meta.local_fields]


class CategoryCodeAdmin(MPTTModelAdmin):
    # specify pixel amount for this ModelAdmin only:
    list_display = [x.name for x in CategoryCode._meta.local_fields]
    mptt_level_indent = 20


admin.site.register(CategoryCode, CategoryCodeAdmin)


@admin.register(NewsAgency)
class NewsAgencyAdmin(admin.ModelAdmin):
    list_display = [x.name for x in NewsAgency._meta.local_fields]


@admin.register(TelegramPost)
class TelegramPostAdmin(admin.ModelAdmin):
    list_display = [x.name for x in TelegramPost._meta.local_fields]
