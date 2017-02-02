from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from app.models import Project
from django.urls import reverse_lazy
from django.http import HttpResponse


# Create your views here.

class ProjectsIndexView(ListView):
    template_name = 'app/project.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.all()


class ProjectCreate(CreateView):
    model = Project
    fields = ['id', 'name', 'key', 'description', 'startDate', 'endDate', 'project_owner']


class ProjectUpdate(UpdateView):
    model = Project
    fields = ['id', 'name', 'key', 'description', 'startDate', 'endDate', 'project_owner']
    template_name_suffix = '_update_form'


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('ProjectsList')