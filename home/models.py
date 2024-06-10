from django.db import models
from django.utils import timezone

# Create your models here.

class FileInfo(models.Model):
    path = models.URLField()
    info = models.CharField(max_length=255)

    def __str__(self):
        return self.path
    
    
class Task(models.Model):
    task=models.CharField(max_length=50, null=True)
    details=models.CharField(max_length=100, null=True)
    completed=models.BooleanField(default=False)
    comletiondate = models.DateTimeField(auto_now_add=False, null=True)
    obs=models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.task
    class Meta:
        ordering = ['-comletiondate']