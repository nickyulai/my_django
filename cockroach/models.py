from django.db import models

class UserModel(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
