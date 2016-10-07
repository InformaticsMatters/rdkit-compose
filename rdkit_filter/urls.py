from django.conf.urls import url
from rdkit_filter import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^pains/?$', views.pains, name='pains'),
]
