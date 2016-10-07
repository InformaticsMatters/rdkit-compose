from django.conf.urls import url

from rdkit_screen import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^screen_simple/?$', views.screen_simple, name='screen_simple')
]
