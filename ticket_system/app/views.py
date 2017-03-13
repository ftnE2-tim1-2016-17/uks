import datetime
from .models import Issue, Comment, Project, RoleOnProject, Status, Priority
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import ModelForm, DateInput
from django.contrib import messages


#
class DateInput(DateInput):
    input_type = 'date'


class IssueFormUpdate(ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'endDate', 'assignedTo', 'project', 'description', 'timeSpent',
                  'donePercentage']
        '''  -- 'status', 'priority', --  '''
        widgets = {
            'startDate': DateInput(),
            'endDate': DateInput(),
        }


class IssueFormCreate(IssueFormUpdate):
    class Meta(IssueFormUpdate.Meta):
        exclude = ('donePercentage', 'timeSpent', )



@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    template_name = 'app/issue_detail.html'
    comment_list = Comment.objects.filter(issue=issue)
    user = request.user
    data = {"issue": issue, "comment_list": comment_list, "user": user}
    return render(request, template_name, data)


@login_required
def issue_create(request):
    template_name = 'app/issue_form.html'
    form = IssueFormCreate(request.POST or None)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.createdBy = request.user
        issue.startDate = datetime.datetime.now()
        issue.donePercentage = 0
        issue.spentTime = 0
        issue.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    return render(request, template_name, {'form': form})


@login_required
def issue_update(request, pk):
    template_name = 'app/issue_update_form.html'
    issue = get_object_or_404(Issue, pk=pk)
    time_spent = issue.timeSpent
    issue.timeSpent = 0
    form = IssueFormUpdate(request.POST or None, instance=issue)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.timeSpent = time_spent + form.cleaned_data['timeSpent']
        issue.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    return render(request, template_name, {'form': form})


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
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'description', 'startDate', 'endDate']
        widgets = {
            'startDate': DateInput(),
            'endDate': DateInput()
        }


@login_required
def project_list(request):
    project = Project.objects.all()
    data = {'project_list': project}
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
