from django.db import models
# Create your models here.


class SW_article(models.Model):
    id = models.IntegerField(primary_key=True) # 需手动设置自动增长
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    href = models.CharField(max_length=500)

class XZ_article(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    href = models.CharField(max_length=500)




