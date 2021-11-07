from django.core.management.base import BaseCommand
from time import time
from django.utils import timezone
from jobs.models import Source
from jobs.scrapers import *


class Command(BaseCommand):
    help = 'Web scraping: get jobs from sources stored in Source table and store them into Job table'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--cron', type=int, help='Use 0 or 1 to simulate that cron is used')
        parser.add_argument('-d', '--debug', type=int, help='Use 0 or 1 to set detailed debugging')

    def handle(self, *args, **kwargs):
        # Prepare variables
        total_start_time = time()
        is_cron = True if 'cron' in kwargs and kwargs['cron'] else False
        if is_cron:
            print(f'Cron triggered at: {str(timezone.now())}')
        debug = True if 'debug' in kwargs and kwargs['debug'] else False

        # Update is_active column to 0
        Job.objects.all().update(is_active=False)

        # Loop through all sources, get data from it and store it in db
        for source in Source.objects.filter(is_active=True):
            if not is_cron:
                print(f'Scraping {source.name}...')
            start_time = time()
            scraper_name = f'{source.name}Scraper'
            try:
                scraper_class = eval(scraper_name)
                scraper_class.run(source, debug)
                diff_time = round(time() - start_time, 1)
                if not is_cron:
                    print(f'Finished {source.name} ({source.url}) in {diff_time}s')
            except Exception as e:
                print(e)

        # Delete deprecated records
        Job.objects.filter(is_active=False).delete()

        # Print general result
        total_diff_time = round(time() - total_start_time, 1)
        new_line = '\n' if not is_cron else ''
        print(f'{new_line}Result: Total Time: {total_diff_time}s')
