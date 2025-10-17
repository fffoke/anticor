from django.db import models

# Create your models here.

class Report(models.Model):
    title = models.CharField(max_length=70, blank = False, null=False) 
    image = models.ImageField(upload_to="images/")
    text = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
    max_length=20,
    choices=[
        ("CRITICAL", "Важная"),
        ("SECONDARY", "Обычная"),
        ("SPAM", "Спам")
    ],
    default="SECONDARY"
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_decided = models.BooleanField(default=False, null=False)
    decided_at = models.DateTimeField(blank=True, null=True)


class Sos(models.Model):
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    iin = models.IntegerField(blank=True)
    name = models.CharField(max_length=70)
    tg_id = models.BigIntegerField(blank=True)
    is_decided = models.BooleanField(default=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(blank=True, null=True)   


