from django.http import HttpResponse
from django.shortcuts import render
from models import *
from constants.app_constants import *
import json

def index(request,pageno=1,category=""):
    pageno=int(pageno)-1
    if len(category)!=0:
       
        no_of_articles=Article.objects.filter(pcategoryid__name__contains=category).count()
    else:
        no_of_articles=Article.objects.count()

    items_on_one_page=NO_OF_ITEMS_ON_A_PAGE
    list_groups = PCategory.get_categories()
    list_article=Article.fetch_articles((pageno)*10, items_on_one_page,category=category)
    list_spotlight_article = Article.get_spotlight_articles(5)
    template_value={}
    if len(category)==0:
        template_value["category"]='Select Categories'
    else:
        template_value["category"]=".........."+category
    template_value["articles"]=list_article
    template_value["groups"]=list_groups
    template_value["page"]=pageno+1
    template_value["totalarticles"]=no_of_articles
    template_value["page_strength"]=items_on_one_page
    template_value["spotlight_article"]=list_spotlight_article
    return render(request, 'reader/home.html', template_value)


def increase_article_count(request):
    if request.method == 'POST':
        try:
            print "***"
            id=request.POST.get("article_id")
            print id
            Article.increase_count(int(id))
            print "successful"
        except Exception:
            print Exception.message 
        return HttpResponse(json.dumps("1"), mimetype="application/x-javascript")
        #return render(request,json.dumps('1'),{})
        #return render(request, 'index.html', {'datas': "1"})
        #return HttpResponse("1", mimetype="application/javascript")