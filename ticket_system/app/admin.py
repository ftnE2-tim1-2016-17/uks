from django.contrib import admin
from .models import Project, Priority, Status, Issue

# Register your models here.

admin.site.register(Project)
admin.site.register(Priority)
admin.site.register(Status)
admin.site.register(Issue)
