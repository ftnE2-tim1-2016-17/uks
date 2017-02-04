from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^ProjectsList$', views.ProjectsIndexView.as_view(), name='project'),
    url(r'^NewProject$', views.ProjectCreate.as_view(), name='project_form'),
    url(r'^EditProject/(?P<pk>\d+)$', views.ProjectUpdate.as_view(), name='project_update_form'),
    url(r'^DeleteProject/(?P<pk>\d+)$', views.ProjectDelete.as_view(), name='project_confirm_delete'),
    url(r'^RoleOnProjectsList$', views.RoleOnProjectsIndexView.as_view(), name='roleOnProject'),
    url(r'^NewUserOnProject$', views.RoleOnProjectCreate.as_view(), name='roleOnProject_form'),
    url(r'^EditUserOnProject/(?P<pk>\d+)$', views.RoleOnProjectUpdate.as_view(), name='roleOnProject_update_form'),
    url(r'^DeleteUserOnProject/(?P<pk>\d+)$', views.RoleOnProjectDelete.as_view(), name='roleOnProject_confirm_delete'),

]

