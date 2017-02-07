import datetime
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import Issue, Comment
from .forms import IssueForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404


class IssueIndexView(generic.ListView):
    template_name = 'app/issues.html'
    context_object_name = 'issue_list'

    def get_queryset(self):
        return Issue.objects.filter(assignedTo=self.request.user, createdBy=self.request.user)


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    template_name = 'app/issue_detail.html'
    comment_list = Comment.objects.filter(issue=issue)
    user = request.user
    data = {"issue": issue, "comment_list": comment_list, "user": user}
    return render(request, template_name, data)


class IssueCreate(CreateView):
    model = Issue
    form_class = IssueForm

    def form_valid(self, form):
        type = 'bla bla'
        form.instance.type = type
        startDate = datetime.datetime.now()
        form.instance.startDate = startDate
        return super(IssueCreate, self).form_valid(form)
    success_url = reverse_lazy('issues')


# IssueUpdateView ?
class IssueUpdate(UpdateView):
    model = Issue
    #fields = ['title', 'startDate', 'endDate', 'createdBy', 'assignedTo', 'project', 'status', 'priority', 'description', 'spentTime', 'donePercentage']
    form_class = IssueForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('issues')
    # in html {% include 'app/form-template.html' %} OR {% bootstrap_form form %}


class IssueDelete(DeleteView):
    model = Issue
    success_url = reverse_lazy('issues')

@login_required
def comment_create(request):
    comment = Comment()
    comment.message = request.POST.get("comment")
    comment.datetime = datetime.datetime.now()
    comment.author = request.user
    issue = Issue.objects.get(pk=request.POST.get("issue_id"))
    comment.issue = issue
    comment.save()
    return HttpResponseRedirect(reverse('issue-detail', kwargs={'pk': issue.id}))