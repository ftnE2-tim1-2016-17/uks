from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from app.models import Priority
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the app index.")


class PriorityCreate(CreateView):
    model = Priority
    fields = ['id', 'name', 'key', 'marker']


class PriorityUpdate(UpdateView):
    model = Priority
    fields = ['id', 'name', 'key', 'marker']
    template_name_suffix = '_update_form'