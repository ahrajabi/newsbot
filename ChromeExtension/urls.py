from django.conf.urls import url, patterns

urlpatterns = [
    url(r'^news/(?P<username>\w+)', 'ChromeExtension.main.chrome_extension_response'),
]
