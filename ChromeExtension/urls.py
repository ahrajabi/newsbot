from django.conf.urls import url, patterns

urlpatterns = [
    url(r'^news/(?P<username>\w+)', 'ChromeExtension.main.chrome_extension_response'),
    url(r'^telegram_codalir/', 'ChromeExtension.main.get_telegram_codal'),
    url(r'^telegram_search/', 'ChromeExtension.main.get_telegram_with_entity'),


]
