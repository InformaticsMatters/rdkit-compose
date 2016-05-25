from django.conf.urls import patterns, url

from proj import views
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    #url(r'^rdkit_cluster/', include('rdkit_cluster.urls',namespace="rdkit_cluster")),
    #url(r'^rdkit_screen/', include('rdkit_screen.urls',namespace="rdkit_screen")),
    #url(r'^docking_runs/', include('docking_runs.urls',namespace="docking_runs")),
    #url(r'^conf_gen/', include('conf_gen.urls',namespace="conf_gen")),
    url(r'^rdkit_filter/', include('rdkit_filter.urls',namespace="rdkit_filter")),
    url(r'^rdkit_conf/', include('rdkit_conf.urls',namespace="rdkit_conf")),
)
