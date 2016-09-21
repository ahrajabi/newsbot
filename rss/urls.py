from django.conf.urls import url, include
from rest_framework import routers
from rss.views import NewsViewSet, schema_view


router = routers.DefaultRouter()
router.register(r'news', NewsViewSet)

urlpatterns = [
    url(r'^docs/', schema_view),
]

urlpatterns += router.urls
