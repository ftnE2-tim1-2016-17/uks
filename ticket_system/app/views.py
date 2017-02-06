import pdb
import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import Issue
from .forms import IssueForm



def test(request):
    #nista = ''

    issue = Issue.objects.filter(assignedTo=request.user, createdBy=request.user)
    pdb.set_trace()
    context = {'issue' : issue[0]}

    return render(request, 'app/test.html', context)

class IssueIndexView(generic.ListView):
    template_name = 'app/issues.html'
    context_object_name = 'issue_list'

    def get_queryset(self):
        return Issue.objects.filter(assignedTo=self.request.user, createdBy=self.request.user)

class IssueDetailView(generic.DetailView):
    model = Issue
    print('bla bla')
    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        print('skenj')
        print(context['issue'].title)
        return context
    template_name = 'app/issue_detail.html'

# IssueCreateView ?
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

