__author__ = 'nasim'
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from rss.models import RssFeeds, CategoryCode, NewsAgency
from rss.ml import normalize
from entities.models import Entity


def add_or_update_entity(name, status, min_should=1, synonym='', related='', positive='', negative='', summary=''):
    obj, created = Entity.objects.update_or_create(name=name,
                                                   defaults={
                                                       'status': status,
                                                       'summary': summary,
                                                       'min_should': min_should
                                                   })
    # SYNONYM
    obj.synonym.clear()
    for item in synonym.split(','):
        inp = item.strip()
        if len(inp) == 0:
            continue
        sobj, screated = Entity.objects.update_or_create(name=inp)
        if screated:
            sobj.status = 'R'
            sobj.save()
        if not sobj in obj.synonym.all():
            obj.synonym.add(sobj)
    # RELATED
    obj.related.clear()
    for item in related.split(','):
        inp = item.strip()
        if len(inp) == 0:
            continue
        robj, rcreated = Entity.objects.update_or_create(name=inp)
        if rcreated:
            robj.status = 'R'
            robj.save()
        if not robj in obj.related.all():
            obj.related.add(robj)
    # POSITIVE
    obj.positive.clear()
    for item in positive.split(','):
        inp = item.strip()
        if len(inp) == 0:
            continue
        pobj, pcreated = Entity.objects.update_or_create(name=inp)
        if pcreated:
            pobj.status = 'R'
            pobj.save()
        if not pobj in obj.positive.all():
            obj.positive.add(pobj)
    # NEGATIVE
    obj.negative.clear()
    for item in negative.split(','):
        inp = item.strip()
        if len(inp) == 0:
            continue
        nobj, ncreated = Entity.objects.update_or_create(name=inp)
        if ncreated:
            nobj.status = 'R'
            nobj.save()
        if not nobj in obj.negative.all():
            obj.negative.add(nobj)

    obj.save()


class Command(BaseCommand):
    help = "for adding new site detail enter datails in rss_list.csv , and execute below store_site_details script"

    #    def add_arguments(self, parser):
    #        parser.add_argument('starting_line', type=int)

    def handle(self, *args, **options):
        """read csv file from starting line to last line"""
        # starting_line = options['starting_line']
        self.get_entities()

    def get_entities(self):
        print("Write Entities details in Database ... ")
        path = os.path.dirname(os.path.abspath(__file__)) + '/../../entities_list.csv'
        # path = '../../../rss_list.csv'
        with open(path) as f:
            reader = list(csv.reader(f))
            print(reader[1][0])
            print(reader[1][1])
            print(reader[1][2])
            print(reader[1][3])
            print(reader[1][4])
            print(reader[1][5])
            print(reader[1][6])
            for row in reader[1:]:
                print(row[0])

                add_or_update_entity(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
