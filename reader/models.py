from django.db import models
import datetime
import feedparser
from dateutil import parser
from time import mktime
from django.db import transaction
from dateutil.tz import *
from math import *
from topia.termextract import extract
from constants.app_constants import *
from common.stemming import *

# Create your models heare.
       
class Site(models.Model):
    name= models.CharField(max_length=200)
    webfeedlink=models.CharField(max_length=400, verbose_name='web feed link')
    softdelete=models.BooleanField(default=True)
    addedon = models.DateTimeField()
    last_published_article_time=models.DateTimeField(verbose_name='last published article time')
    
    def _get_all_articles_published_after_last_sync_time(self):
        print self.webfeedlink
        parsedData=feedparser.parse(self.webfeedlink)
     
        articles=[]
        last_published_article_time= self.last_published_article_time
        image_title=""
        image_url=""
        image_href=""
        try:
            image=parsedData.feed.image
            if "title" in image:
                image_title=image["title"]
            if "link" in image:
                image_url=image["link"]
            if "href" in image:
                image_href=image["href"]
        except AttributeError:
            # no image attribute
            pass
        
        list_category = PCategory.get_categories()
        dict_features = Features.get_fetaures() 
        #count=0  
        for entry in parsedData.entries:
            article=Article()
            article.image_url=image_url
            article.image_href=image_href
            article.image_title=image_title
            article.header=entry.title
            article.link=entry.link
            article.count=0
            article.description=entry.description.encode('utf-8')
            try:
                article.published=parser.parse(entry.published)
            except:
                current_date_time = datetime.datetime.now()
                article.published = datetime.datetime(current_date_time.year,current_date_time.month,current_date_time.day, current_date_time.hour, current_date_time.minute,current_date_time.second, tzinfo=tzutc())
                pass
            article.siteid=self
            article.get_pcategory(list_category, dict_features)
            if not article.published.tzinfo or not article.published.tzinfo.utcoffset:
                temp_date = article.published
                article.published = datetime.datetime(temp_date.year,temp_date.month,temp_date.day, temp_date.hour, temp_date.minute,temp_date.second, tzinfo=tzutc())
            if article.published>self.last_published_article_time:
                articles.append(article)
                if article.published>last_published_article_time:
                    last_published_article_time=article.published
            current_date_time = datetime.datetime.now()
            article.addedon = datetime.datetime(current_date_time.year,current_date_time.month,current_date_time.day, current_date_time.hour, current_date_time.minute,current_date_time.second, tzinfo=tzutc())

            #count=count+1
                    
            
        
        #changing site last article published time
        self.last_published_article_time=last_published_article_time
        return articles
   
    def save_articles_published_after_last_sync_time(self):
        articles=self._get_all_articles_published_after_last_sync_time()
        with transaction.atomic():
            self.save()
            print "check"
            Article.objects.bulk_create(articles)
   
            
            

    def fetch_articles(self,offset_from_latest=0,no_of_articles=10):
        query=Article.objects.filter(siteid = self).order_by("-published")[offset_from_latest:no_of_articles]
        articles=[]
        for article in query:
            articles.append(article)
        return articles


class SiteProbability(models.Model):
    siteid=models.ForeignKey(Site)
    probability=models.FloatField()
    
class PCategory(models.Model):
    name=models.CharField(max_length=100)
    @staticmethod
    def get_categories():
        query=PCategory.objects.all()
        list_category=[]
        for element in query:
            list_category.append(element)
        return list_category
            

class Features(models.Model):
    name=models.CharField(max_length=200)
    pcategory=models.ForeignKey(PCategory)
    probability=models.FloatField()
    
    @staticmethod
    def get_fetaures():
        query= Features.objects.all()
        dict_features={}
        for element in query:
            feature_name = element.name
            if feature_name in dict_features:
                dict_features[feature_name].append(element)
            else:
                dict_features[feature_name]= [element]
        return dict_features
   
       
class Article(models.Model):
    header=models.CharField(max_length=200)
    description=models.CharField(max_length=1000000)
    author = models.CharField(max_length=50,null=True)
    siteid= models.ForeignKey(Site)
    pcategoryid=models.ForeignKey(PCategory,verbose_name='primary category id') 
    image_url= models.CharField(max_length=300, null=True)
    image_href= models.CharField(max_length=300, null=True)
    image_title=models.CharField(max_length=300, null=True)
    link= models.CharField(max_length=300, null=True)
    addedon=models.DateTimeField()
    published = models.DateTimeField()
    count = models.IntegerField()
    
    @staticmethod
    def delete_articles():
        count=Article.objects.count()
        if count>MAX_NO_OF_ARTICLES_ALLOWED:
            objects_to_keep=Article.objects.order_by("-published")[:MAX_NO_OF_ARTICLES_ALLOWED]
            Article.objects.exclude(pk__in=objects_to_keep).delete()      
    
    @staticmethod
    def increase_count(id):
        print "increased_count"
        entry=Article.objects.get(id=id)
        print entry.count
        entry.count=entry.count+1
        entry.save()
        entry=Article.objects.get(id=id)
        print entry.count
        print "increased"
    
    @staticmethod
    def get_spotlight_articles(count):
        query=Article.objects.select_related().order_by("-count")[:count]
        articles=[]
        for article in query:
            articles.append(article)
        return articles
    
    @staticmethod
    def fetch_articles(offset_from_latest=0,no_of_articles=10,category=""):
        start_point = offset_from_latest-1
        end_point = start_point + no_of_articles
        if len(category)==0:
            if start_point<0:
                query=Article.objects.select_related().order_by("-published")[:end_point]
            else:
                query=Article.objects.select_related().order_by("-published")[start_point:end_point]
        else:

            if start_point<0:
                query=Article.objects.filter(pcategoryid__name__contains=category).select_related().order_by("-published")[:end_point]
            else:
                query=Article.objects.filter(pcategoryid__name__contains=category).select_related().order_by("-published")[start_point:end_point]

        articles=[]
        for article in query:
        
            articles.append(article)
        return articles
    
    
    
    def getImportaantFeatures(self):
        extractor=extract.TermExtractor()
        extractor.filter=extract.permissiveFilter
        key_word_for_desc=extractor(self.description)
        dict_important_features={}
        for element in key_word_for_desc:
            word = stem_word(element[0])
            if len(word)!=0:
                dict_important_features[word]=element[1]
        
        #print str(dict_important_features)
        return dict_important_features
    
    def get_pcategory(self,list_pcategory,dict_features):
        important_features=self.getImportaantFeatures()
        dict_scores_for_category={}
      
        for feature in important_features.keys():
            if feature in dict_features:
                for element in dict_features[feature]:
                    category= element.pcategory.name
                    score_value = element.probability
                    score_value=score_value+DELTA
#                     print category
#                     print feature
#                     print score_value
#                     print "*****"
                    log_value = important_features[feature]*log(score_value,10)
                    if category in dict_scores_for_category:
                        dict_scores_for_category[category]=dict_scores_for_category[category]+log_value
                    else:
                        dict_scores_for_category[category]=log_value
                        
        print dict_scores_for_category
        min_value = log(MIN_LIMIT,10)
        print min_value
        p_category_key=None
    
        for key in dict_scores_for_category.keys():
            if dict_scores_for_category[key]>=min_value:
                min_value = dict_scores_for_category[key]
                p_category_key = key
        
        if p_category_key==None:
            p_category_key=OTHER_KEY
        
        #print p_category_key
        for element in list_pcategory:    
            if element.name.lower().strip()==p_category_key.lower().strip():
                self.pcategoryid=element
           
                
        
            
                
            
            
            
        
    
    

