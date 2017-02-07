from django.forms import ModelForm, DateInput
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy, reverse
from app.models import Project, RoleOnProject

# Create your views here.


class DateInput(DateInput):
    input_type = 'date'


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
