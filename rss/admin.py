from django.contrib import admin

from .models import RssFeeds, News, BaseNews, ImageUrls, NewsLike, CategoryCode, NewsAgency


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


@admin.register(CategoryCode)
class CategoryCodeAdmin(admin.ModelAdmin):
    list_display = [x.name for x in CategoryCode._meta.local_fields]


@admin.register(NewsAgency)
class NewsAgencyAdmin(admin.ModelAdmin):
    list_display = [x.name for x in NewsAgency._meta.local_fields]

