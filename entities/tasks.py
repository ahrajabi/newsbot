import wikipedia
from telegram import user
from rss.ml import word_tokenize
from telegrambot.models import UserProfile, UserLiveNews

from .models import UserEntity, Entity, NewsEntity
from telegrambot.models import UserLiveNews


# wikipedia.set_lang('fa')

#
# def get_entity_contain(name):
#     wik = wikipedia.search(name, results=3, suggestion=True)
#     ret = list()
#     print(wik[0])
#     for item in wik[0]:
#         ent = Entity.objects.filter(wiki_name=item)
#         if not ent:
#             try:
#                 wiki_page = wikipedia.page(item, redirect=True, auto_suggest=True)
#                 ent = Entity.objects.create(name=item, wiki_name=item, status='P',
#                                             summary=wiki_page.summary)
#                 ret.append(ent)
#             except wikipedia.exceptions.DisambiguationError as e:
#                 wiki_page = wikipedia.page(e.options, redirect=True, auto_suggest=True)
#                 ent = Entity.objects.create(name=e.options, wiki_name=e.options, status='P',
#                                             summary=wiki_page.summary)
#                 ret.append(ent)
#
#         else:
#             ret.extend(ent)
#     return ret


# def get_entity(e_id):
#     s = Entity.objects.filter(id=e_id)
#     if not s:
#         return None
#     return s[0]


def get_user_entity(user):
    return [i.entity for i in UserEntity.objects.filter(user=user, status=True)]


def get_link(user, entity):
    if entity in get_user_entity(user):
        return "/remove_" + str(entity.id) + " " + entity.name + " "
    else:
        return "/add_"+str(entity.id)+" " + entity.name + ""


def set_entity(user, entity_id, mark=True):
    ent = Entity.objects.get(pk=entity_id)
    if not ent:
        return False

    ue = UserEntity.objects.filter(entity=ent, user=user)

    if not ue:
        user.userentity_set.create(entity=ent, status=(mark == True)).save()
        return True
    else:
        for i in ue:
            i.status = (mark == 1)
            i.save()
        return True


#
# def set_score_entity(user, entity_id, score=0):
#     ent = Entity.objects.get(pk=entity_id)
#     ue = UserEntity.objects.filter(entity=ent, user=user)
#     if not ent or not ue:
#         return False
#     for item in ue:
#         item.score = score
#         item.save()
#     return True


#َWe can use of yield for get running function!
def get_entity_news(news):
    entity = Entity.objects.filter(status__in=['N', 'P', 'A'])

    news_ent = []
    for en in entity:
        word_list = [en.name]
        word_list += [syn.name for syn in en.synonym.all()]
        word_occurrence = 0

        for word in word_list:
            if word in word_tokenize(news.base_news.title) or word in word_tokenize(news.summary) or\
                            word in word_tokenize(news.body):
                word_occurrence +=1

            if word_occurrence >= en.min_should:
                news_ent.append({'entity': en, 'score': 1})
                NewsEntity.objects.create(news=news, entity=en, score=1)
                en.news_count +=1
                en.latest_news = news
                en.save()
                break
    return news_ent


def live_entity_news(news, news_ent):
    ent = [item['entity'] for item in news_ent]
    ue = UserEntity.objects.filter(entity__in=ent, status=True)
    users = list(set([item.user for item in ue]))
    ups = UserProfile.objects.filter(user_settings__live_news=True,
                                     stopped=False,
                                     activated=True)
    us = [item.user for item in ups]

    for u in users:
        if u in us:
            UserLiveNews.objects.create(user=u, news=news)


def get_entity_text(input_text):
    # TODO fix entitis , now و is entity !
    ent = Entity.objects.filter(status__in=['N', 'P', 'A'])
    ret = []
    for entity in ent:
        if entity.name in input_text:
            ret.append(entity)
    return ret
