import os

from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from multiselectfield import MultiSelectField

from helper import convert


def _delete_image(instance):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
            temp = instance.image.path.split('.')
            temp = temp[0] + '.webp'
            if os.path.isfile(temp):
                os.remove(temp)


class Collection(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, default='')
    image = models.ImageField(upload_to='collections/', blank=True)
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    custom = models.BooleanField(default=False, help_text="Nem aktivált funkció, azt jelöli, hogy a kollekció azok "
                                                          "közé tartozik-e, amelyeket a vásárlók módosíthatnak. "
                                                          "Pl. névkezdőbetűs nyaklánc, stb.")
    show_on_home_page = models.BooleanField(default=True, help_text="Látható legyen-e a kollekció a főoldalon")
    basic_collection = models.BooleanField(default=False, help_text="Alap kollekció jelölő")
    regular_collection = models.BooleanField(default=False, help_text="Állandó kollekció jelölő")
    studio_collection = models.BooleanField(default=False, help_text="Kollekció, amely összefogja az "
                                                                     "összes olyan terméket, amelyik csak a "
                                                                     "studióban elérhető")
    best_seller_collection = models.BooleanField(default=False, help_text="Best seller kollekció jelölő")
    seo_title = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO title a google crawler számára. "
                                                             "Ez látszik a böngésző tabon, ha rávisszük az egeret.")
    seo_description = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO description a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")
    seo_keywords = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO keywords a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")
    seo_image_alt = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO alt a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)
        convert()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Kollekció'
        verbose_name_plural = 'Kollekciók'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:products_view', args=[self.slug])


@receiver(models.signals.post_delete, sender=Collection)
def auto_delete_collection_image_on_delete(sender, instance, **kwargs):
    _delete_image(instance)


STUD_CHOICES = ((1, 'NORMAL'),
                (2, 'NICKEL_FREE'),
                (3, 'PLASTIC'))

KEY_RING_CHOICES = ((1, 'KEREK'),
                    (2, 'KARABINER'),
                    (3, 'SZIV'))

DELIVERY_SIZES = ((1, 'S'),
                  (2, 'M'),
                  (3, 'L'))


class Product(models.Model):
    collection = models.ForeignKey(Collection, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, default='')
    image = models.ImageField(blank=True)
    description = models.TextField(blank=True)
    size = models.TextField(blank=True)
    price = models.IntegerField()
    stock = models.IntegerField(blank=True, default=0)
    studs = MultiSelectField(choices=STUD_CHOICES, max_choices=3, default=STUD_CHOICES[0], null=True, blank=True)
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price_api_id = models.CharField(max_length=50, default='')
    key_ring = MultiSelectField(choices=KEY_RING_CHOICES, max_choices=3, default=KEY_RING_CHOICES[0], max_length=50)
    custom = models.BooleanField(default=False)
    custom_date = models.BooleanField(default=False)
    initials = models.BooleanField(default=False)
    delivery_size = MultiSelectField(choices=DELIVERY_SIZES, max_choices=1, min_choices=1, default=DELIVERY_SIZES[0],
                                     null=True)
    seo_title = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO title a google crawler számára. "
                                                             "Ez látszik a böngésző tabon, ha rávisszük az egeret.")
    seo_description = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO description a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")
    seo_keywords = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO keywords a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")
    seo_image_alt = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO alt a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)
        convert()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Termék'
        verbose_name_plural = 'Termékek'
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.collection.slug, self.slug])

    def get_stud_value(self, value):
        values = ['nemesacél alap', 'nikkelmentes fülbevaló alap - fém',
                  'műanyag fülbevaló alap - fém mentes']
        return values[int(value) - 1]

    def get_key_ring_value(self, value):
        values = ['kerek kulcskarika - 25mm', 'karabíner - 32mm', 'szív alakú kulcskarika - 28mm']
        return values[int(value) - 1]


@receiver(models.signals.post_delete, sender=Product)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    _delete_image(instance)


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


@receiver(models.signals.post_delete, sender=Image)
def auto_delete_image_image_on_delete(sender, instance, **kwargs):
    _delete_image(instance)


class ProductType(models.Model):
    product = models.ForeignKey(Product, related_name='product_types', on_delete=models.CASCADE)
    color = models.CharField(max_length=200)
    color_hex = models.CharField(max_length=7, default='#FFFFFF')
    stock = models.PositiveIntegerField()
    image = models.ImageField(blank=True)
    seo_image_alt = models.CharField(
        max_length=200, db_index=True, blank=True, help_text="SEO alt a google crawler számára. "
                                                             "Ez sehol sem látszik a weboldalon.")

    class Meta:
        ordering = ('color',)
        verbose_name = 'Terméktípus'
        verbose_name_plural = 'Terméktípusok'

    def save(self, *args, **kwargs):
        super(ProductType, self).save(*args, **kwargs)
        convert()

    def __str__(self):
        return self.color


@receiver(models.signals.post_delete, sender=ProductType)
def auto_delete_type_image_on_delete(sender, instance, **kwargs):
    _delete_image(instance)


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
    slug = models.SlugField(max_length=200, db_index=True, unique=True, default='')
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
    name = models.TextField(max_length=2000, default='')

    class Meta:
        verbose_name = 'Üzenet'
        verbose_name_plural = 'Üzenetek'

    def __str__(self):
        return self.subject
