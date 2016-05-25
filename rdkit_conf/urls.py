from django.conf.urls import patterns, url
from rdkit_conf import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^gen_confs/?$', views.gen_confs, name='gen_confs'),
)
