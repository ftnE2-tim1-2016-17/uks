from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new$', views.PriorityCreate.as_view(), name='priority_form'),
    url(r'^edit/(?P<pk>\d+)$', views.PriorityUpdate.as_view(), name='priority_update_form'),
]

