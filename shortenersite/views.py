from django.shortcuts import render_to_response, get_object_or_404
import random, string, json
from shortenersite.models import Urls
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.context_processors import csrf


def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('shortenersite/index.html', c)


def redirect_original(request, short_id):
    url = get_object_or_404(Urls, pk=short_id)  # get object, if not found return 404 error
    url.count += 1
    url.save()
    return HttpResponseRedirect(url.httpurl)


def shorten_url(request):
    url = request.POST.get("url", '')
    if not (url == ''):
        short_id = get_short_code()
        b = Urls(httpurl=url, short_id=short_id)
        b.save()

        response_data = {}
        response_data['url'] = settings.SITE_URL + "/r/" + short_id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    return HttpResponse(json.dumps({"error": "error occurs"}),
                        content_type="application/json")


def shorten(url):
    if not (url == ''):
        try:
            short_id = Urls.objects.get(httpurl=url).short_id
        except Urls.DoesNotExist:
            short_id = get_short_code()
            b = Urls(httpurl=url, short_id=short_id)
            b.save()
        return settings.SITE_URL + "/r/" + short_id
    return 0


def get_short_code():
    length = 6
    char = string.ascii_uppercase + string.digits + string.ascii_lowercase
    # if the randomly generated short_id is used then generate next
    while True:
        short_id = ''.join(random.choice(char) for x in range(length))
        try:
            temp = Urls.objects.get(pk=short_id)
        except:
            return short_id
