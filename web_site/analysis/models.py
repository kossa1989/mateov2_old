from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Analyses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    config = models.TextField()
    query_sm = models.TextField()
    name = models.CharField(max_length=150)
    schema = models.CharField(max_length=50)
    case_group = models.CharField(max_length=200)
    permissive = models.BooleanField(default=False)

class Runs(models.Model):
    analysis = models.ForeignKey(Analyses, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
