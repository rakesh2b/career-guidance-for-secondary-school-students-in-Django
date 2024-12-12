# main/models.py

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=100, choices=[
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts')
    ])

class AptitudeTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    domain = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    user_answer = models.CharField(max_length=100)
