from django.contrib import admin
from .models import Project, Priority, Status, Issue, Issue_chart, Closed_Issue_chart, Issue_for_user

# Register your models here.

admin.site.register(Project)
admin.site.register(Priority)
admin.site.register(Status)
admin.site.register(Issue)
admin.site.register(Issue_chart)
admin.site.register(Closed_Issue_chart)
admin.site.register(Issue_for_user)