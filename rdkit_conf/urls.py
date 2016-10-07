from django.conf.urls import url
from rdkit_conf import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^gen_confs/?$', views.gen_confs, name='gen_confs')
]
