from enum import Enum

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField


class Collection(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='collections/', blank=True)
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Kollekció'
        verbose_name_plural = 'Kollekciók'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:products_view', args=[self.name])


class StudTypeEnum(Enum):
    NORMAL = 0
    NICKEL_FREE = 1
    PLASTIC = 2


STUD_CHOICES = ((1, 'NORMAL'),
                (2, 'NICKEL_FREE'),
                (3, 'PLASTIC'))


class Product(models.Model):
    collection = models.ForeignKey(Collection, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(blank=True)
    description = models.TextField(blank=True)
    size = models.TextField(blank=True)
    price = models.IntegerField()
    stock = models.IntegerField(blank=True, default=0)
    studs = MultiSelectField(choices=STUD_CHOICES, max_choices=3, default=STUD_CHOICES[0])
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price_api_id = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Termék'
        verbose_name_plural = 'Termékek'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id])

    def get_stud_value(self, value):
        values = ['normál fülbevaló alap - fém', 'nikkelmentes fülbevaló alap - fém',
                  'műanyag fülbevaló alap - fém mentes']
        return values[int(value) - 1]


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', default=None)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('product',)
        verbose_name = 'Kép'
        verbose_name_plural = 'Képek'

    def __str__(self):
        return self.product.name + " Img"


class ProductType(models.Model):
    product = models.ForeignKey(Product, related_name='product_types', on_delete=models.CASCADE)
    color = models.CharField(max_length=200)
    color_hex = models.CharField(max_length=7, default='#FFFFFF')
    stock = models.PositiveIntegerField()
    image = models.ImageField(blank=True)

    class Meta:
        ordering = ('color',)
        verbose_name = 'Terméktípus'
        verbose_name_plural = 'Terméktípusok'

    def __str__(self):
        return self.color


class VariationManager(models.Manager):
    def all(self):
        return super(VariationManager, self).filter(available=True)

    def studs(self):
        return self.all().filter(attribute='stud')

    def colors(self):
        return self.all().filter(attribute='color')


VAR_CATEGORIES = (
    ('color', 'color'),
    ('stud', 'stud'),
)


class Notification(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    text = models.CharField(max_length=200, db_index=True)

    def save(self, *args, **kwargs):
        if not self.pk and Notification.objects.exists():
            raise ValidationError('Only one notification instance can be saved.')
        return super(Notification, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Értesítés'
        verbose_name_plural = 'Értesítések'

    def __str__(self):
        return self.name


PRICE_CHOICES = ((1000, '1000'),
                 (2000, '2000'),
                 (5000, '5000'),
                 (10000, '10000'))


class GiftCard(models.Model):
    name = models.CharField(max_length=200, db_index=True, default='Ajándékkártya')
    price = models.IntegerField()
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price_api_id = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Ajándékkártya'
        verbose_name_plural = 'Ajándékkártyák'

    def __str__(self):
        return self.name


class Message(models.Model):
    subject = models.CharField(max_length=200, default='')
    email = models.EmailField(default='')
    message = models.TextField(max_length=2000, default='')
    sender = models.CharField(max_length=200, default='')
    created = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Üzenet'
        verbose_name_plural = 'Üzenetek'

    def __str__(self):
        return self.subject