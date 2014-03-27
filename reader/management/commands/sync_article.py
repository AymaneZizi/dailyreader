from reader.models import *
from django.core.management.base import BaseCommand, CommandError
import os
MAX_ARTICLES_IN_DATABASE=500

class Command(BaseCommand):
    def handle(self,*args, **options):
        all_sites=Site.objects.all()
        for site in all_sites:
            site.save_articles_published_after_last_sync_time()