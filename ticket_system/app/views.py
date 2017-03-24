import datetime
import json
from .models import Issue, Comment, Project, RoleOnProject, Status, IssueChange, Issue_chart, Closed_Issue_chart, \
    Issue_for_user
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.forms import ModelForm
from django.contrib import messages
from django.shortcuts import render_to_response
from chartit import DataPool, Chart
from urllib.request import urlopen
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm


@login_required
def issueschart(request, pk):
    charts = Issue_chart.objects.all()
    for chart in charts:
        chart.delete()

    project = get_object_or_404(Project, pk=pk)
    status_open = Status.objects.filter(name='New')
    status_resolved = Status.objects.filter(name='Resolved')
    status_closed = Status.objects.filter(name='Closed')
    open_issues_for_project = Issue.objects.filter(project=project, status=status_open[0])
    resolved_issues_for_project = Issue.objects.filter(project=project, status=status_resolved[0])
    closed_issues_for_project = Issue.objects.filter(project=project, status=status_closed[0])
    opened_model = Issue_chart(1, 1, len(open_issues_for_project))
    opened_model.save()
    resolved_model = Issue_chart(2, 2, len(resolved_issues_for_project))
    resolved_model.save()
    closed_model = Issue_chart(3, 3, len(closed_issues_for_project))
    closed_model.save()

    def issue_status(num):
        status = {1: 'opened', 2: 'resolved', 3: 'closed'}
        return status[num]

    issuedata = \
        DataPool(
            series=
            [{'options': {
                'source': Issue_chart.objects.all()},
              'terms': [
                  'num',
                  'quantity']}
             ])

    cht = Chart(
        datasource=issuedata,
        series_options=
        [{'options': {
            'type': 'pie',
            'stacking': False},
          'terms': {
              'num': [
                  'quantity']
          }}],
        chart_options=
        {'title': {
            'text': 'Opened/resolved/closed issues for project'}},
        x_sortf_mapf_mts=(None, issue_status, False))

    # Step 3: Send the chart object to the template.
    return render_to_response('app/graphs.html', {'issueschart': cht, 'project': project})


@login_required
def user_closed_issues_chart(request, pk):
    charts = Closed_Issue_chart.objects.all()
    for chart in charts:
        chart.delete()

    current_user = request.user
    project = get_object_or_404(Project, pk=pk)
    status_closed = Status.objects.filter(name='Closed')
    issues = Issue.objects.filter(project=project, assignedTo=current_user, status=status_closed)
    for issue in issues:
        print(issue.finishDate)
        if Closed_Issue_chart.objects.filter(date=issue.finishDate):
            closed_chart = Closed_Issue_chart.objects.filter(date=issue.finishDate)
            closed_chart = closed_chart[0]
            closed_chart.num += 1
            closed_chart.save()
        else:
            closed_chart = Closed_Issue_chart()
            closed_chart.date = issue.finishDate
            closed_chart.num = 1
            closed_chart.save()

    ds = DataPool(
        series=
        [{'options': {
            'source': Closed_Issue_chart.objects.all()},
          'terms': [
              'date',
              'num']}
         ])

    cht = Chart(
        datasource=ds,
        series_options=
        [{'options': {
            'type': 'line',
            'stacking': False},
          'terms': {
              'date': [
                  'num']
          }}],
        chart_options=
        {'title': {
            'text': 'Number of closed issues for user on project'},
         'xAxis': {
             'title': {
                 'text': 'Finish dates'}}})

    return render_to_response('app/graphs.html', {'issueschart': cht, 'project': project})


@login_required
def issues_for_user(request, pk):
    charts = Issue_for_user.objects.all()
    for chart in charts:
        chart.delete()

    project = get_object_or_404(Project, pk=pk)
    issues_for_project = Issue.objects.filter(project=project)

    for issue in issues_for_project:
        bla = Issue_for_user.objects.all()
        if not bla:
            issue_FU = Issue_for_user()
            issue_FU.username = issue.assignedTo.username
            issue_FU.numOfI = 1
            issue_FU.save()
        else:
            for b in bla:
                if issue.assignedTo.username == b.username:
                    b.numOfI += 1
                    b.save()
                    break
                else:
                    issue_FU = Issue_for_user()
                    issue_FU.username = issue.assignedTo.username
                    issue_FU.numOfI = 1
                    issue_FU.save()

    def issue_dict(username):
        dict = {}
        for issue in issues_for_project:
            dict[issue.assignedTo.username] = issue.assignedTo.username
        return dict[username]

    issuedata = \
        DataPool(
            series=
            [{'options': {
                'source': Issue_for_user.objects.all()},
              'terms': [
                  'username',
                  'numOfI']}
             ])

    cht = Chart(
        datasource=issuedata,
        series_options=
        [{'options': {
            'type': 'pie',
            'stacking': False},
          'terms': {
              'username': [
                  'numOfI']
          }}],
        chart_options=
        {'title': {
            'text': 'Assigned issues for users on project'}},
        x_sortf_mapf_mts=(None, issue_dict, False))

    # Step 3: Send the chart object to the template.
    return render_to_response('app/graphs.html', {'issueschart': cht, 'project': project})


@login_required
def git_commit(request, pkProj, pkIssue):

    try:
        project = get_object_or_404(Project, pk=pkProj)
        issue = get_object_or_404(Issue, pk=pkIssue)

        url = project.git + '/commits?sha=master'
        response = urlopen(url)

        string = response.read().decode('utf-8')
        json_obj = {}
        json_obj = json.loads(string)
    except Exception:
        return redirect('bad_git_url')
    commit_list = []
    template_name = 'app/commit_list.html'
    for l in json_obj:
        a = l['commit']['message']
        a = a.split(' ')
        ht = '#' + str(issue.id)
        if a[0] == ht or a[len(a) - 1] == ht:
            commit_list.append(l['commit']['message'])
            print(l['commit']['message'])
    return render(request, template_name, {'commit_list': commit_list, 'project': project})


class DateInput(forms.DateInput):
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
    return render(request, template_name, {'form': form, 'project': project})


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

        # code for saving issue history
        old_issue = UpdateIssueGetAndSet.issue_to_update
        # create history item from ordinary char fields value
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

        if issue.status.name == 'Closed':
            issue.finishDate = datetime.datetime.now()
        issue.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('project_detail', kwargs={'pk': issue.project.id}))
    issue.timeSpent = time_spent
    UpdateIssueGetAndSet.issue_to_update = issue
    return render(request, template_name, {'form': form, 'project': project})


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
    return render(request, template_name, {'issue': issue, 'project': issue.project.id})


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
        return redirect('project_detail', pk=project.id)
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
    def __init__(self, project, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = self.fields['project'].queryset.filter(id__in=project)

    class Meta:
        model = RoleOnProject
        fields = ['id', 'role', 'user', 'project']


@login_required
def role_on_project_list(request):
    project = Project.objects.filter(project_owner=request.user)
    role_on_project_list = []
    project_list = []
    for i, c in enumerate(project):
        project_list.append(c)
    for project in project_list:
        one_role_on_project = RoleOnProject.objects.filter(project=project)
        for i, c in enumerate(one_role_on_project):
            role_on_project_list.append(c)
    role_on_project_filter_by_user_and_role = RoleOnProject.objects.filter(user=request.user, role="administrator")
    for i, c in enumerate(role_on_project_filter_by_user_and_role):
        role = RoleOnProject.objects.filter(project=c.project)
        for j, k in enumerate(role):
            if k not in role_on_project_list:
                role_on_project_list.append(k)
    data = {'roleOnProject_list': role_on_project_list}
    template_name = 'app/roleOnProject.html'
    return render(request, template_name, data)

@login_required
def role_on_project_create(request):
    role_of_projects = RoleOnProject.objects.all()
    template_name = 'app/roleOnProject_form.html'
    project = []
    project_filter_by_owner = Project.objects.filter(project_owner=request.user)
    for i, c in enumerate(project_filter_by_owner):
        if c.id not in project:
            project.append(c.id)
    project_filter_by_admin_role = RoleOnProject.objects.filter(user=request.user, role="administrator")
    for i, c in enumerate(project_filter_by_admin_role):
        if c.project.id not in project:
            project.append(c.project.id)
    print(project)
    form = RoleOnProjectForm(project, request.POST or None)
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
    form = RoleOnProjectForm(request.user, request.POST or None, instance=role_on_project)
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
        #form = RoleOnProjectForm(initial={'project': project.id})
        form = RoleOnProjectForm([project.id])

    return render(request, template_name, {'form': form})


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


@login_required()
def user_profile(request):
    template_name = 'app/user_profile.html'
    return render(request, template_name, {'user': request.user})


@login_required
def user_update(request):
    template_name = 'app/user_profile_update.html'
    user = get_object_or_404(User, pk=request.user.id)
    form = UserChangeForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('user-profile')
    return render(request, template_name, {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'app/change_password.html', {'form': form})
