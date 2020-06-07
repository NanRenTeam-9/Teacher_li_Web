from django.db import models


# Create your models here.

class history(models.Model):
    ds = models.DateTimeField(null=False, primary_key=True)
    confirm = models.IntegerField(null=True)
    confirm_add = models.IntegerField(null=True)
    suspect = models.IntegerField(null=True)
    suspect_add = models.IntegerField(null=True)
    heal = models.IntegerField(null=True)
    heal_add = models.IntegerField(null=True)
    dead = models.IntegerField(null=True)
    dead_add = models.IntegerField(null=True)


class details(models.Model):
    update_time = models.DateTimeField(null=True)
    province = models.CharField(max_length=15, null=True)
    city = models.CharField(max_length=15, null=True)
    confirm = models.IntegerField(null=True)
    confirm_add = models.IntegerField(null=True)
    heal = models.IntegerField(null=True)
    dead = models.IntegerField(null=True)
