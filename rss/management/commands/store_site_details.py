__author__ = 'nasim'
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from rss.models import RssFeeds, CategoryCode, NewsAgency

class Command(BaseCommand):
    help = "for adding new site detail enter datails in rss_list.csv , and execute below store_site_details script"

    def add_arguments(self, parser):
        parser.add_argument('starting_line', type=int)

    def handle(self, *args, **options):
        """read csv file from starting line to last line"""
        starting_line = options['starting_line']
        print("Write rss details in Database ... ")
        path = os.path.dirname(os.path.abspath(__file__)) + '/../../rss_list.csv'
        #path = '../../../rss_list.csv'
        with open(path) as f:
            reader = list(csv.reader(f))
            for row in reader[starting_line-1:]:
                print(row[7])
                obj_site, created = NewsAgency.objects.update_or_create(name=row[1],
                                                                        defaults={'url': row[0],
                                                                                  'fa_name': row[2],
                                                                                  'selector': row[8],
                                                                                  'summary_selector': row[9],
                                                                                  'image_selector': row[10],
                                                                                  'time_delay': (row[11] == 'True')})
                obj_cat, created = CategoryCode.objects.update_or_create(name=row[5],
                                                                         defaults={'fa_name': row[3]})
                if not row[7]:
                    continue
                obj, created = RssFeeds.objects.update_or_create(main_rss=row[7],
                                                                 defaults={'category': row[3],
                                                                           'activation': (row[4] == 'True'),
                                                                           'category_ref': obj_cat,
                                                                           'order': row[6],
                                                                           'news_agency': obj_site})
