from reader.models import *
from django.core.management.base import BaseCommand, CommandError
import os
import feedparser
import re
MAX_ARTICLES_IN_DATABASE=500


urls=[
"http://msdn.microsoft.com/en-us/magazine/rss/default.aspx?z=z&iss=1",
"http://blogs.msdn.com/b/mainfeed.aspx",
"http://www.asp.net/rss/spotlight",
"http://visualstudiomagazine.com/rss-feeds/blogs.aspx"
"http://feeds.feedburner.com/IbmDataManagementMagazine",
"http://www.databasejournal.com/icom_includes/feeds/dbjournal/dbjournal-features-10.xml",
"http://sqlmag.com/rss.xml"
"http://feeds.feedburner.com/mobile-tuts-summary?format=xml",
"http://html5weekly.com/rss/1h963k8n",
"http://javascriptweekly.com/rss/1anc165m",
"http://feeds.feedburner.com/mobileindustryreview?format=xml",
"http://justanapplication.wordpress.com/feed/",
"http://mobilephonedevelopment.com/feed/",
"http://feeds2.feedburner.com/IphoneDevelopment?format=xml",
"http://feeds2.feedburner.com/MobileOrchard?format=xml"
"http://codegoop.com/feed/",
"http://www.developer.com/icom_includes/feeds/developer/dev-java-25.xml",
"http://feeds.feedburner.com/DevxLatestJavaArticles?format=xml",
"http://feeds.dzone.com/dzone/java?format=xml",
"http://www.eclipse.org/home/eclipseinthenews.rss",
"http://feeds.oreilly.com/oreilly/java?format=xml",
"http://feeds.dzone.com/javalobby/frontpage?format=xml",
"http://www.theserverside.com/rss/forum.tss?forum_id=2?format=xml",
"http://www.artima.com/spotlight/feeds/spotlight.rss?format=xml"



]


def parse_data_from_html_description(description):
    return_value=""
    loop_in_tag=0
    count=0
    description=re.sub(' +',' ',description)
    description=description.replace("\r"," ")
    description=description.replace("\n"," ")
    description=description.replace("\r\n"," ")
    description=description.replace("\t"," ")
    description=description.replace("\0"," ")
    description=description.replace("\x0B"," ")
    description=description.replace(chr(10)," ")
    description=description.replace(chr(13)," ")
    for character in description:
        try:
            if character=="<":
                loop_in_tag=1
            elif character==">":
                loop_in_tag=0
            elif description[count]+description[count+1]+description[count+2]+description[count+3]=="&lt;":
                loop_in_tag=1
            elif description[count-3]+description[count-2]+description[count-1]+description[count]=="&gt;":
                loop_in_tag=0  
            elif loop_in_tag==0:
                return_value=return_value+character
            count=count+1
        except:
            count=count+1
            pass
        
    return return_value

class Command(BaseCommand):
    def handle(self,*args, **options):
        with open(os.getcwd()+"\\reader\\management\\commands\\"+"NET1.csv","wb") as file:
            for url in urls:
                feed=feedparser.parse(url)
                for article in feed.entries:
                    description=article.description.encode("utf-8")
                    data_in_description=parse_data_from_html_description(description)
                    row='"'+data_in_description+'"'+",Java"+"\r\n"
                    file.write(row)