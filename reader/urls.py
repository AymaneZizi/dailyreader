from django.conf.urls import patterns, url

from reader import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^page/(?P<pageno>\d+)$', views.index, name='index'),
    url(r'^category/(?P<category>[a-zA-Z0-9% ]+)$', views.index, name='index'),
     url(r'^category/(?P<category>[a-zA-Z0-9% ]+)/page/(?P<pageno>\d+)$', views.index, name='index'),
    url(r'^increase_count', views.increase_article_count, name='index'),
  

)