from django.conf.urls import patterns, url
from rdkit_filter import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^pains/?$', views.pains, name='pains'),
)
