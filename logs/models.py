from django.db import models


class LogFile(models.Model):
    type = models.CharField(max_length=50, default='')
    message = models.TextField(max_length=2000, default='')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logok'
