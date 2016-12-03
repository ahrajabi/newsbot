from rss.ml import word_tokenize, remove_no_text, bi_gram, tri_gram
from telegrambot.models import UserProfile
from entities.models import UserEntity, Entity, NewsEntity
from telegrambot.models import UserLiveNews


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


def get_entity_news(news):
    entity = Entity.objects.filter(status__in=['N', 'P', 'A'])

    news_ent = []
    for en in entity:
        word_list = [en.name]
        word_list += [syn.name for syn in en.synonym.all()]
        word_occurrence = 0

        for word in word_list:
            text = remove_no_text(news.body)
            check_list = word_tokenize(text)
            check_list.extend(bi_gram(text))
            check_list.extend(tri_gram(text))

            if word in check_list:
                word_occurrence += 1
            if word_occurrence >= en.min_should:
                news_ent.append({'entity': en, 'score': 1})
                NewsEntity.objects.create(news=news, entity=en, score=1)
                en.news_count += 1
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
