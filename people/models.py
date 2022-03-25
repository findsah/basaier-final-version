from django.db import models


# Create your models here.
class People(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "People"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
