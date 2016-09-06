import wikipedia
from telegram.emoji import Emoji

from .models import UserEntity, Entity, NewsEntity
wikipedia.set_lang('fa')


def get_entity_contain(name):
    wik = wikipedia.search(name, results=3, suggestion=True)
    ret = list()
    print(wik[0])
    for item in wik[0]:
        ent = Entity.objects.filter(wiki_name=item)
        if not ent:
            try:
                wiki_page = wikipedia.page(item, redirect=True, auto_suggest=True)
                ent = Entity.objects.create(name=item, wiki_name=item, status='P',
                                            summary=wiki_page.summary)
                ret.append(ent)
            except wikipedia.exceptions.DisambiguationError as e:
                wiki_page = wikipedia.page(e.options, redirect=True, auto_suggest=True)
                ent = Entity.objects.create(name=e.options, wiki_name=e.options, status='P',
                                            summary=wiki_page.summary)
                ret.append(ent)

        else:
            ret.extend(ent)
    return ret


def get_entity(e_id):
    s = Entity.objects.filter(id=e_id)
    if not s:
        return None
    return s[0]


def get_user_entity(user):
    return [i.entity for i in UserEntity.objects.filter(user=user, status=True)]


def get_link(user, entity):
    if entity in get_user_entity(user):
        return "/remove_" + str(entity.id) + " " + entity.name + " "
    else:
        return "/add_"+str(entity.id)+" " + entity.name + ""


def set_entity(user, entity_id, mark='Follow'):
    ent = Entity.objects.get(pk=entity_id)
    if not ent:
        return False

    ue = UserEntity.objects.filter(entity=ent, user=user)

    if not ue:
        user.userentity_set.create(entity=ent, status=(mark == 1)).save()
        return True
    else:
        for i in ue:
            i.status = (mark == 1)
            i.save()
        return True


def set_score_entity(user, entity_id, score=0):
    ent = Entity.objects.get(pk=entity_id)
    ue = UserEntity.objects.filter(entity=ent, user=user)
    if not ent or not ue:
        return False
    for item in ue:
        item.score = score
        item.save()
    return True

#َWe can use of yield for get running function!
def get_entity_news(news_list):
    ent = Entity.objects.filter(status__in=['N', 'P', 'A'])
    ret = []
    for news in news_list:
        news_ent = []
        for entity in ent:
            score = 0
            if entity.name in news.base_news.title:
                score = 3
                news_ent.append({'id': entity.id, 'score': score})
            elif entity.name in news.summary:
                score = 2
                news_ent.append({'id': entity.id, 'score': score})
            elif entity.name in news.body:
                score = 1
                news_ent.append({'id': entity.id, 'score': score})
            if score > 0:
                NewsEntity.objects.create(news=news, entity=entity, score=score)
                entity.news_count += 1
                entity.latest_news = news
                entity.save()
        ret.append((news.id, news_ent))

    return ret


def get_entity_text(input_text):
    # TODO fix entitis , now و is entity !
    ent = Entity.objects.filter(status__in=['N', 'P', 'A'])
    ret = []
    for entity in ent:
        if entity.name in input_text:
            ret.append(entity)
    return ret


def prepare_advice_entity_link(entity):
    return Emoji.SMALL_ORANGE_DIAMOND + "/add_"+str(entity.id)+" " + entity.name + ""
