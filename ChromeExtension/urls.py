from django.conf.urls import url, patterns

urlpatterns = [
    url(r'^news/(?P<user_id>\d+)', 'ChromeExtension.main.chrome_extension_response'),
]
