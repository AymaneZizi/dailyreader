from django.contrib import admin
from reader.models import Article,Site

# Register your models here.

    
class SiteAdmin(admin.ModelAdmin):
    fields=[
            "name",
            "webfeedlink",
            "softdelete",
            "addedon",
            "last_published_article_time"
            ]
    list_display = ('name',"webfeedlink","softdelete","addedon","last_published_article_time")



class ArticleAdmin(admin.ModelAdmin):
    fields=[
            "header",
    "description",
    "author",
    "siteid",
    "pcategoryid", 
    "image_url",
    "image_href",
    "image_title",
    "link",
    "addedon",
    "published"
            ]
    list_display = (  "header",
    "description",
    "author",
    "siteid",
    "pcategoryid", 
    "image_url",
    "image_href",
    "image_title",
    "link",
    "addedon",
    "published")


admin.site.register(Site,SiteAdmin)
admin.site.register(Article,ArticleAdmin)