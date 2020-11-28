import uuid

from django.db import models


class BoughtGiftCard(models.Model):
    unique_uuid = models.CharField(max_length=36, db_index=True)
    price = models.IntegerField()
    active = models.BooleanField(default=False)
    bought = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()

    def save(self, *args, **kwargs):
        self.unique_uuid = uuid.uuid4()
        return super(BoughtGiftCard, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Megvásárolt ajándékkártya'
        verbose_name_plural = 'Megvásárolt ajándékkártyák'
