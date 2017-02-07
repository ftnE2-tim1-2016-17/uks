import datetime
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import Issue, Comment, Project, RoleOnProject
from .forms import IssueForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import ModelForm, DateInput


class DateInput(DateInput):
    input_type = 'date'


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


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'description', 'startDate', 'endDate', 'project_owner']
        widgets = {
            'startDate' : DateInput(),
            'endDate' : DateInput()
        }

def project_list(request):
    project = Project.objects.all()
    data = {'project_list': project}
    template_name = 'app/project.html'
    return render(request, template_name, data)


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    template_name = 'app/projectDetails.html'
    data = {"project": project}
    return render(request, template_name, data)


def project_create(request):
    template_name = 'app/project_form.html'
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': project.id}))
    return render(request, template_name, {'form': form})


def project_update(request, pk):
    template_name = 'app/project_update_form.html'
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('project')
    return render(request, template_name, {'form': form})


def project_delete(request, pk):
    template_name = 'app/project_confirm_delete.html'
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project')
    return render(request, template_name, {'project': project})


class RoleOnProjectForm(ModelForm):
    class Meta:
        model = RoleOnProject
        fields = ['id', 'role', 'user', 'project']


def role_on_project_list(request):
    role_of_project = RoleOnProject.objects.all()
    data = {'roleOnProject_list': role_of_project}
    template_name = 'app/roleOnProject.html'
    return render(request, template_name, data)


def role_on_project_create(request):
    template_name = 'app/roleOnProject_form.html'
    form = RoleOnProjectForm(request.POST or None)
    if form.is_valid():
        role_on_project = form.save(commit=False)
        role_on_project.save()
        form.save_m2m()
        return redirect('roleOnProject')
    return render(request, template_name, {'form': form})


def role_on_project_update(request, pk):
    template_name = 'app/roleOnProject_update_form.html'
    role_on_project = get_object_or_404(RoleOnProject, pk=pk)
    form = RoleOnProjectForm(request.POST or None, instance=role_on_project)
    if form.is_valid():
        form.save()
        return redirect('roleOnProject')
    return render(request, template_name, {'form': form})


def role_on_project_delete(request, pk):
    template_name = 'app/roleOnProject_confirm_delete.html'
    role_on_project = get_object_or_404(RoleOnProject, pk=pk)
    if request.method == 'POST':
        role_on_project.delete()
        return redirect('roleOnProject')
    return render(request, template_name, {'roleonproject': role_on_project})


def role_on_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = RoleOnProjectForm(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')
    else:
        form = RoleOnProjectForm(initial={'project': project.id})

    return render(request, 'app/roleOnProject_form.html', {'form': form})
