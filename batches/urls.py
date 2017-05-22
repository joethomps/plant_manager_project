from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^new/$', views.new_batch, name='new_batch'),
    url(r'^(?P<batch_no>[0-9]+)/edit/$', views.edit_batch, name='edit_batch'),
    url(r'^(?P<batch_no>[0-9]+)/delete/$', views.delete_batch, name='delete_batch'),
    url(r'^(?P<batch_no>[0-9]+)/$', views.batch_detail, name='batch_detail'),
    url(r'^(?P<batch_no>[0-9]+)/ticket/$', views.ticket, name='ticket'),

    url(r'^recipes/$', views.recipes, name='recipes'),
    url(r'^recipes/new/$', views.new_recipe, name='new_recipe'),
    url(r'^recipes/(?P<recipe_id>[0-9]+)/edit/$', views.edit_recipe, name='edit_recipe'),
    url(r'^recipes/(?P<recipe_id>[0-9]+)/delete/$', views.delete_recipe, name='delete_recipe'),
    url(r'^recipes/(?P<recipe_id>[0-9]+)/copy/$', views.copy_recipe, name='copy_recipe'),
    
    url(r'^(?P<model>clients|drivers|trucks|ingredients|locations)/$', views.generics, name='generics'),
    url(r'^(?P<model>clients|drivers|trucks|ingredients|)/new/$', views.new_generic, name='new_generic'),
    url(r'^(?P<model>clients|drivers|trucks|ingredients|locations)/(?P<id>[0-9]+)/edit/$', views.edit_generic, name='edit_generic'),
    url(r'^(?P<model>clients|drivers|trucks|ingredients|locations)/(?P<id>[0-9]+)/delete$', views.delete_generic, name='delete_generic'),
]
