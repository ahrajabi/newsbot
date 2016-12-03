from django.shortcuts import render
from entities.models import Entity
from rss.elastic import news_with_terms
from rss.models import News
from django import forms
from django.views.generic.edit import FormView

# Create your views here.


def symbols(request):
    en = Entity.objects.filter(status='A').order_by('name')
    return render(request, "symbols.html", {'items': en})


def symbols_id(request, entity_id):
    en = Entity.objects.get(status='A', id=entity_id)
    en_news = news_with_terms(entity_list=[en],
                              size=100,
                              start_time='now-100d',
                              sort='published_date')
    try:
        news_ent = [item['_id'] for item in en_news['hits']['hits']]
    except KeyError:
        # raise ValueError('invalid news')
        return 0

    response = []
    for news_id in news_ent:
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            continue

        response.append(news)

    return render(request, "symbols-id.html", {'items': response})


class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass


class symbols_test(FormView):
    template_name = 'symbols-test.html'
    form_class = ContactForm
    success_url = '/thanks/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(symbols_test, self).form_valid(form)



