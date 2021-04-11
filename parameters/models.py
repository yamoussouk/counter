from django.db import models


class Parameter(models.Model):
    name = models.CharField(default='', max_length=100)
    value = models.CharField(default='', max_length=200)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        if self.active:
            raise PermissionError("Cannot delete parameter which are currently active")
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name = 'Paraméter'
        verbose_name_plural = 'Paraméterek'
