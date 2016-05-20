from django.conf.urls import patterns, url
from conf_gen import views

urlpatterns = patterns('',
    url(r'^get_confs/$', views.get_confs, name='get_confs'),
)
