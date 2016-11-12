__author__ = 'nasim'
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from rss.models import RssFeeds, CategoryCode, NewsAgency
from rss.ml import normalize
from entities.models import Entity
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
            for row in reader[1:]:
                print(row[0])
                obj, created = Entity.objects.update_or_create(name=row[0],
                                                               defaults={
                                                                   'status': row[1],
                                                                   'summary': row[6],
                                                               })
                for item in row[2].split(','):
                    inp = item.strip()
                    sobj, screated = Entity.objects.update_or_create(name=inp)
                    if screated:
                        sobj.status = 'R'
                        sobj.save()
                    if not sobj in obj.synonym.all():
                        obj.synonym.add(sobj)

                for item in row[3].split(','):
                    inp = item.strip()
                    robj, rcreated = Entity.objects.update_or_create(name=inp)
                    if rcreated:
                        robj.status = 'R'
                        robj.save()
                    if not robj in obj.related.all():
                        obj.related.add(robj)

                obj.save()
