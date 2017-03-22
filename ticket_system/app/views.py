import datetime
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Issue, Comment, Project, RoleOnProject, IssueChange, MonthlyWeatherByCity
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.forms import ModelForm, DateInput
from django.contrib import messages
from django.shortcuts import render_to_response
from chartit import DataPool, Chart


def weatherchart(request):
    weatherdata = \
        DataPool(
            series=
            [{'options': {
                'source': MonthlyWeatherByCity.objects.all()},
              'terms': [
                  'month',
                  'houston_temp',
                  'boston_temp']}
             ])

    cht = Chart(
        datasource=weatherdata,
        series_options=
        [{'options': {
            'type': 'line',
            'stacking': False},
          'terms': {
              'month': [
                  'boston_temp',
                  'houston_temp']
          }}],
        chart_options=
        {'title': {
            'text': 'Weather Data of Boston and Houston'},
         'xAxis': {
             'title': {
                 'text': 'Month number'}}})

    # Step 3: Send the chart object to the template.
    return render_to_response('app/graphs.html', {'weatherchart': cht})


class DateInput(DateInput):
    input_type = 'date'


class IssueFormUpdate(ModelForm):
    def __init__(self, project_users_ids, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['assignedTo'].queryset = self.fields['assignedTo'].queryset.filter(id__in=project_users_ids)

    type = forms.CharField(required=False)

    class Meta:
        model = Issue
        fields = ['title', 'status', 'priority', 'type', 'endDate', 'assignedTo', 'description', 'timeSpent',
                  'donePercentage']

        widgets = {
            'endDate': DateInput(),
        }


class IssueFormCreate(IssueFormUpdate):
    class Meta(IssueFormUpdate.Meta):
        fields = ['title', 'status', 'priority', 'type', 'endDate', 'assignedTo', 'description']


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    template_name = 'app/issue_detail.html'
    comment_list = Comment.objects.filter(issue=issue)
    user = request.user
    data = {"issue": issue, "comment_list": comment_list, "user": user}
    return render(request, template_name, data)


@login_required
def issue_create(request, pk):
    template_name = 'app/issue_form.html'
    project = get_object_or_404(Project, pk=pk)
    project_users_ids = [project.project_owner.id]

    roles_on_projects = RoleOnProject.objects.filter(project=project)
    for i, c in enumerate(roles_on_projects):
        if c.user.id not in project_users_ids:
            project_users_ids.append(c.user.id)

    form = IssueFormCreate(project_users_ids, request.POST or None)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.createdBy = request.user
        issue.startDate = datetime.datetime.now()
        issue.donePercentage = 0
        issue.spentTime = 0
        issue.project = project
        issue.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    return render(request, template_name, {'form': form})


class UpdateIssueGetAndSet:
    def __init__(self):
        self.issue_to_update = None


@login_required
def issue_update(request, pk):
    template_name = 'app/issue_update_form.html'
    issue = get_object_or_404(Issue, pk=pk)
    time_spent = issue.timeSpent
    issue.timeSpent = 0
    project = issue.project
    project_users_ids = [project.project_owner.id]

    roles_on_projects = RoleOnProject.objects.filter(project=project)
    for i, c in enumerate(roles_on_projects):
        if c.user.id not in project_users_ids:
            project_users_ids.append(c.user.id)
    form = IssueFormUpdate(project_users_ids, request.POST or None, instance=issue)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.timeSpent = time_spent + form.cleaned_data['timeSpent']

        #code for saving issue history
        old_issue = UpdateIssueGetAndSet.issue_to_update
        #create history item from ordinary char fields value
        for attr_update in (vars(issue)).items():
            for attr in (vars(old_issue)).items():
                if (attr[0] == attr_update[0]) and (attr[1] != attr_update[1]):
                    if (attr_update[0] != "_state") and (attr_update[0] != "status_id") and \
                            (attr_update[0] != "assignedTo_id") and (attr_update[0] != "priority_id"):
                        issue_history = IssueChange()
                        issue_history.author = request.user
                        issue_history.datetime = datetime.datetime.now()
                        issue_history.issue = issue
                        issue_history.propertyName = attr_update[0]
                        issue_history.oldValue = attr[1]
                        issue_history.newValue = attr_update[1]
                        issue_history.save()
        #create issue history when changing foreign key value
        if old_issue.priority != issue.priority:
            issue_history = IssueChange()
            issue_history.author = request.user
            issue_history.datetime = datetime.datetime.now()
            issue_history.issue = issue
            issue_history.propertyName = "priority"
            issue_history.oldValue = str(old_issue.priority)
            issue_history.newValue = str(issue.priority)
            issue_history.save()
        if old_issue.status != issue.status:
            issue_history = IssueChange()
            issue_history.author = request.user
            issue_history.datetime = datetime.datetime.now()
            issue_history.issue = issue
            issue_history.propertyName = "status"
            issue_history.oldValue = str(old_issue.status)
            issue_history.newValue = str(issue.status)
            issue_history.save()
        if old_issue.assignedTo != issue.assignedTo:
            issue_history = IssueChange()
            issue_history.author = request.user
            issue_history.datetime = datetime.datetime.now()
            issue_history.issue = issue
            issue_history.propertyName = "assigned to"
            issue_history.oldValue = str(old_issue.assignedTo)
            issue_history.newValue = str(issue.assignedTo)
            issue_history.save()
        #end of code for saving issue history

        issue.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    issue.timeSpent = time_spent
    UpdateIssueGetAndSet.issue_to_update = issue
    return render(request, template_name, {'form': form})


@login_required
def issue_history(request, pk):
    template_name = 'app/issue_history.html'
    issue = get_object_or_404(Issue, pk=pk)
    issue_history = IssueChange.objects.filter(issue=issue).order_by("-datetime")
    return render(request, template_name, {'issue_history': issue_history, 'issue': issue})


@login_required
def issue_delete(request, pk):
    template_name = 'app/issue_confirm_delete.html'
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        issue.delete()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    return render(request, template_name, {'issue': issue})


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
    validator = URLValidator()
    git = forms.CharField(required=False, validators=[validator])

    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'description', 'startDate', 'endDate', 'git']
        widgets = {
            'startDate': DateInput(),
            'endDate': DateInput()
        }


@login_required
def project_list(request):
    projects = []
    roles_on_projects = RoleOnProject.objects.filter(user=request.user)
    owned_projects = Project.objects.filter(project_owner=request.user)
    for i, c in enumerate(owned_projects):
        projects.append(c)

    for i, c in enumerate(roles_on_projects):
        if c.project not in projects:
            projects.append(c.project)
    data = {'project_list': projects}
    template_name = 'app/project.html'
    return render(request, template_name, data)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    issue_list_for_project = Issue.objects.filter(project=project)
    template_name = 'app/projectDetails.html'
    data = {"project": project, "issue_list": issue_list_for_project}
    return render(request, template_name, data)


@login_required
def project_create(request):
    template_name = 'app/project_form.html'
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.project_owner = request.user
        project.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': project.id}))
    return render(request, template_name, {'form': form})


@login_required
def project_update(request, pk):
    template_name = 'app/project_update_form.html'
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('project')
    return render(request, template_name, {'form': form})


@login_required
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


@login_required
def role_on_project_list(request):
    role_of_project = RoleOnProject.objects.all()
    data = {'roleOnProject_list': role_of_project}
    template_name = 'app/roleOnProject.html'
    return render(request, template_name, data)


@login_required
def role_on_project_create(request):
    role_of_projects = RoleOnProject.objects.all()
    template_name = 'app/roleOnProject_form.html'
    form = RoleOnProjectForm(request.POST or None)
    if form.is_valid():
        for i, c in enumerate(role_of_projects):
            if (form.cleaned_data['user'] == c.user) and (form.cleaned_data['project'] == c.project):
                messages.error(request, "User: " + str(c.user) + " are already on project: " + str(c.project) + "!")
                return render(request, template_name, {'form': form})
        role_on_project = form.save(commit=False)
        role_on_project.save()
        form.save_m2m()
        return redirect('roleOnProject')
    return render(request, template_name, {'form': form})


@login_required
def role_on_project_update(request, pk):
    role_of_projects = RoleOnProject.objects.all()
    template_name = 'app/roleOnProject_update_form.html'
    role_on_project = get_object_or_404(RoleOnProject, pk=pk)
    form = RoleOnProjectForm(request.POST or None, instance=role_on_project)
    if form.is_valid():
        for i, c in enumerate(role_of_projects):
            if (form.cleaned_data['user'] == c.user) and (form.cleaned_data['project'] == c.project):
                messages.error(request, "User: " + str(c.user) + " are already on project: " + str(c.project) + "!")
                return render(request, template_name, {'form': form})
        form.save()
        return redirect('roleOnProject')
    return render(request, template_name, {'form': form})


@login_required
def role_on_project_delete(request, pk):
    template_name = 'app/roleOnProject_confirm_delete.html'
    role_on_project = get_object_or_404(RoleOnProject, pk=pk)
    if request.method == 'POST':
        role_on_project.delete()
        return redirect('roleOnProject')
    return render(request, template_name, {'roleonproject': role_on_project})


@login_required
def role_on_project(request, pk):
    role_of_projects = RoleOnProject.objects.all()
    template_name = 'app/roleOnProject_form.html'
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = RoleOnProjectForm(request.POST)
        if form.is_valid():
            for i, c in enumerate(role_of_projects):
                if (form.cleaned_data['user'] == c.user) and (form.cleaned_data['project'] == c.project):
                    messages.error(request, "User: " + str(c.user) + " are already on project: " + str(c.project) + "!")
                    return render(request, template_name, {'form': form})
            role_on_project = form.save(commit=False)
            role_on_project.save()
            form.save_m2m()
            return redirect('roleOnProject')
    else:
        form = RoleOnProjectForm(initial={'project': project.id})

    return render(request, template_name, {'form': form})
