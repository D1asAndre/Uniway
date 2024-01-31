from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class DashboardPermission(models.Model):
    class Meta:
        permissions = [
            ("view_dashboard", "Can view dashboard"),
    ] 
