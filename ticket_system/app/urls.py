from django.conf.urls import url
from app import views

#app_name = 'app'

urlpatterns = [
    url(r'^issue/$', views.IssueIndexView.as_view(), name='issues'),
    url(r'^issue/(?P<pk>\d+)$', views.issue_detail, name='issue-detail'),
    url(r'^issue/add/$', views.IssueCreate.as_view(), name='issue-add'),
    url(r'^issue/update/(?P<pk>[0-9]+)/$', views.IssueUpdate.as_view(), name='issue-update'),
    url(r'^issue/(?P<pk>[0-9]+)/delete/$', views.IssueDelete.as_view(), name='issue-delete'),

    url(r'^comment/$', views.comment_create, name='comment-create')
]


