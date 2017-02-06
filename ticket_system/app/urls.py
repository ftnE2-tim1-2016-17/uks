from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^Project/(?P<pk>\d+)$', views.project_detail, name='project_detail'),
    url(r'^ProjectsList$', views.project_list, name='project'),
    url(r'^NewProject$', views.project_create, name='project_form'),
    url(r'^EditProject/(?P<pk>\d+)$', views.project_update, name='project_update_form'),
    url(r'^DeleteProject/(?P<pk>\d+)$', views.project_delete, name='project_confirm_delete'),
    url(r'^RoleOnProjectsList$', views.role_on_project_list, name='roleOnProject'),
    url(r'^NewUserOnProject$', views.role_on_project_create, name='roleOnProject_form'),
    url(r'^NewUserOnProjectFromProject/(?P<pk>\d+)$', views.role_on_project, name='roleOnProjectFromProject_form'),
    url(r'^EditUserOnProject/(?P<pk>\d+)$', views.role_on_project_update, name='roleOnProject_update_form'),
    url(r'^DeleteUserOnProject/(?P<pk>\d+)$', views.role_on_project_delete, name='roleOnProject_confirm_delete'),

]

