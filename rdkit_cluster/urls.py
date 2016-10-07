from django.conf.urls import url

from rdkit_cluster import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cluster_simple/?$', views.cluster_simple, name='cluster_simple')
]

