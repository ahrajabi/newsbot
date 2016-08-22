__author__ = 'nasim'
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from rss.models import RssFeeds

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
                RssFeeds.objects.update_or_create(url=row[0],
                                                  defaults={'name':row[1],
                                                            'fa_name':row[2],
                                                            'main_rss':row[3],
                                                            'selector':row[4],
                                                            'summary_selector':row[5],
                                                            'image_selector':row[6]})
