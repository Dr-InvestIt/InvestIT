from django.db import models

# Create your models here.
class Stock(models.Model):
    ticker1       = models.CharField(max_length=10)
    ticker2       = models.CharField(max_length=10)
