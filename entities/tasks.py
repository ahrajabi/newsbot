from .models import UserEntity, Entity
import wikipedia
wikipedia.set_lang('fa')

def get_entity_contain(Name):
    wik = wikipedia.search(Name, results=3, suggestion=True)
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

def get_entity(ID):
    s = Entity.objects.filter(id=ID)
    if not s:
        return None
    return s[0]

def get_user_entity(User):
    return [i.entity for i in UserEntity.objects.filter(user=User, status=True)]

def get_link(user, entity):
    if entity in get_user_entity(user) :
        return "/remove_" + str(entity.id) +" " + entity.name + " "
    else:
        return "/add_"+str(entity.id)+" " + entity.name + ""


def set_entity(User, entity_id, mark ='Fallow'):
    ent = Entity.objects.get(pk=entity_id)
    if not ent:
        return False

    ue = UserEntity.objects.filter(entity=ent, user=User)

    if not ue :
        User.userentity_set.create(entity= ent, status=(mark == 'Fallow')).save()
        return True
    else:
        for i in ue:
            i.status = (mark == 'Fallow')
            i.save()
        return True


def set_score_entity(User, entity_id,Score=0):
    ent = Entity.objects.get(pk=entity_id)
    ue = UserEntity.objects.filter(entity=ent, user=User)
    if not ent or not ue:
        return False
    for item in ue:
        item.score = Score
        item.save()
    return True

