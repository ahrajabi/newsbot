__author__ = 'nasim'
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from rss.models import RssFeeds, CategoryCode

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
                obj_cat, created = CategoryCode.objects.update_or_create(name=row[5], defaults={'fa_name': row[3],})
                obj, created = RssFeeds.objects.update_or_create(main_rss=row[7],
                                                  defaults={'url': row[0],
                                                            'name': row[1],
                                                            'fa_name': row[2],
                                                            'category': row[3],
                                                            'activation': row[4],
                                                            'category_ref': obj_cat,
                                                            'order': row[6],
                                                            'selector': row[8],
                                                            'summary_selector': row[9],
                                                            'image_selector': row[10]})
