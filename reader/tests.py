from django.test import TestCase
from models import *

# Create your tests here.
class SiteTestCase(TestCase):
    def test_site_fetching_rss_feed_working(self):
        site = Site()
        site.url="http://msdn.microsoft.com/en-us/magazine/rss/default.aspx?z=z&iss=1"
        articles = site.get_all_articles_published_after_last_sync_time()


        