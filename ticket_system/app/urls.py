from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.project_list, name='project'),
    url(r'^issue/(?P<pk>\d+)$', views.issue_detail, name='issue-detail'),
    url(r'^issue/add/(?P<pk>\d+)$', views.issue_create, name='issue-add'),
    url(r'^issue/update/(?P<pk>\d+)/$', views.issue_update, name='issue-update'),
    url(r'^issue/delete/(?P<pk>\d+)$', views.issue_delete, name='issue-delete'),
    url(r'^issue/history/(?P<pk>\d+)$', views.issue_history, name='issue-history'),
    url(r'^comment/$', views.comment_create, name='comment-create'),
    url(r'^project/(?P<pk>\d+)$', views.project_detail, name='project_detail'),
    url(r'^projects/list$', views.project_list, name='project'),
    url(r'^project/add$', views.project_create, name='project_form'),
    url(r'^project/update/(?P<pk>\d+)$', views.project_update, name='project_update_form'),
    url(r'^project/delete/(?P<pk>\d+)$', views.project_delete, name='project_confirm_delete'),
    url(r'^role/list$', views.role_on_project_list, name='roleOnProject'),
    url(r'^role/add$', views.role_on_project_create, name='roleOnProject_form'),
    url(r'^project/role/add/(?P<pk>\d+)$', views.role_on_project, name='roleOnProjectFromProject_form'),
    url(r'^role/update/(?P<pk>\d+)$', views.role_on_project_update, name='roleOnProject_update_form'),
    url(r'^role/delete/(?P<pk>\d+)$', views.role_on_project_delete, name='roleOnProject_confirm_delete'),
    url(r'^issue/commit/(?P<pkProj>\d+)/(?P<pkIssue>\d+)$', views.git_commit, name='commits'),

    url(r'^charts/(?P<pk>\d+)$', views.issueschart, name='chartView'),
    url(r'^charts2/(?P<pk>\d+)$', views.user_closed_issues_chart, name='chartView2'),
    url(r'^charts3/(?P<pk>\d+)$', views.issues_for_user, name='chartView3')

]

