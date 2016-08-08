from .models import UserEntity, Entity

def get_entity(Name):
    if Entity.objects.filter(name__contains=Name):
        ent = Entity.objects.filter(name__contains=Name)
        print(ent)
        return ent
    return None

def set_entity(User, entity_id, mark ='Fallow'):
    ent = Entity.objects.get(pk=entity_id)
    if not ent:
        return False
    if not UserEntity.objects.filter(entity=ent,user=User):
        User.userentity_set.create(entity= ent, status=(mark == 'Fallow')).save()
        return True
    else:
        ue = UserEntity.objects.filter(entity=ent,user=User)
        for i in ue:
            i.status = (mark == 'Fallow')
            i.save()
        return True
