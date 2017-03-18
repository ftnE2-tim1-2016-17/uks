from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

SILVER = "default"
BLUE = "primary"
GREEN = "success"
LIGHT_BLUE = "info"
YELLOW = "warning"
RED = "danger"
MARKER_CHOICES = (
    (SILVER, 'silver'),
    (BLUE, 'blue'),
    (GREEN, 'green'),
    (LIGHT_BLUE, 'light blue'),
    (YELLOW, 'yellow'),
    (RED, 'red')
)

ADMIN = "administrator"
DEVELOPER = "programmer"
QA = "quality assurance"
ROLE = (
    (ADMIN, "admin"),
    (DEVELOPER, "developer"),
    (QA, "qa")
)


class Project(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(unique=True, max_length=10)
    project_owner = models.ForeignKey(to=User, null=False, related_name="owners")
    contributors = models.ManyToManyField(to=User, blank=True, related_name="contributors")
    description = models.TextField()
    startDate = models.DateField()
    endDate = models.DateField()
    git = models.URLField(max_length=1024, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project')


class Status(models.Model):
    name = models.CharField(max_length=30)
    key = models.CharField(unique=True, max_length=10)
    marker = models.CharField(max_length=20, choices=MARKER_CHOICES, default=SILVER)

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=30)
    key = models.CharField(unique=True, max_length=10)
    marker = models.CharField(max_length=20, choices=MARKER_CHOICES, default=SILVER)

    def __str__(self):
        return self.name


'''class Issue_chart(models.Model):
    opened = models.IntegerField()
    closed = models.IntegerField()'''

class Issue_chart(models.Model):
    num = models.IntegerField()
    quantity = models.IntegerField()

class Issue(models.Model):
    type = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=100)
    startDate = models.DateField()
    endDate = models.DateField()
    createdBy = models.ForeignKey(to=User, null=False, related_name="createdIssues")
    assignedTo = models.ForeignKey(to=User, null=False, related_name="assignedIssues")
    project = models.ForeignKey(to=Project, null=False)
    description = models.TextField()
    status = models.ForeignKey(to=Status, null=True)
    priority = models.ForeignKey(to=Priority, null=True)
    timeSpent = models.PositiveIntegerField(default=0, validators=[
        MinValueValidator(0)
    ])
    donePercentage = models.PositiveIntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])


class RoleOnProject(models.Model):
    role = models.CharField(max_length=20, choices=ROLE)
    user = models.ForeignKey(to=User, null=False, related_name="roleOnProject")
    project = models.ForeignKey(to=Project, null=False, related_name="roles")

    def get_absolute_url(self):
        return reverse('roleOnProject')


class HistoryItem(models.Model):
    datetime = models.DateTimeField()
    author = models.ForeignKey(to=User, null=False, related_name="historyItem")
    issue = models.ForeignKey(to=Issue, null=False, related_name="historyItemIssue")


class Comment(HistoryItem):
    message = models.TextField()

    def __str__(self):
        return self.message


class Commit(HistoryItem):
    link = models.URLField()


class IssueChange(HistoryItem):
    propertyName = models.CharField(max_length=50)
    oldValue = models.CharField(max_length=50)
    newValue = models.CharField(max_length=50)






