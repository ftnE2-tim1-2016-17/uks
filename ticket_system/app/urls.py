from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^ProjectsList$', views.ProjectsIndexView.as_view(), name='project'),
    url(r'^NewProject$', views.ProjectCreate.as_view(), name='project_form'),
    url(r'^EditProject/(?P<pk>\d+)$', views.ProjectUpdate.as_view(), name='project_update_form'),
    url(r'^DeleteProject/(?P<pk>\d+)$', views.ProjectDelete.as_view(), name='project_confirm_delete'),
]

