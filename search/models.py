from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class SearchHistory(models.Model):
    keyword = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now=True, )
    result = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

