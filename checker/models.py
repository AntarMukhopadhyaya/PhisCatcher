from django.db import models

# Create your models here.
class PhisWebsite(models.Model):
  class Status(models.IntegerChoices):
    Phish =-1, 'Phish'
    Suspicious = 0 , 'Suspicious'

    NotPhish = 1, 'NotPhish'
  id = models.AutoField(primary_key=True)
  site_name = models.CharField(max_length=255,unique=True)
  url_length = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  having_at = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  double_slash_redirecting = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  HavingHyphen = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  age_of_domain = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  Favicon = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  Request_URL = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  Page_Rank  = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  Google_Index  = models.IntegerField(default=Status.Suspicious,choices=Status.choices)
  def __str__(self):
    return self.site_name

