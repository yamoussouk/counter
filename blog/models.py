from django.db import models
from django.utils.text import slugify

from helper import convert

STATUS = (
    (0, "Draft"),
    (1, "Published")
)

TEMPLATES = (
    (0, "Only text"),
    (1, "Content-image"),
    (2, "Content-next-image")
)


class BlogCategory(models.Model):
    title = models.CharField(max_length=200, db_index=True, unique=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Blog kategória'
        verbose_name_plural = 'Blog kategóriák'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(BlogCategory, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/%s/' % self.slug


def get_upload_path(instance, filename):
    return f'images/blog/{instance.post.slug}/{filename}'


def get_post_upload_path(instance, filename):
    return f'images/blog/{instance.slug}/{filename}'


class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True, unique=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='blog_posts')
    cover_image = models.ImageField(upload_to=get_post_upload_path, blank=True)
    cover_image_alt = models.CharField(max_length=200, blank=True)
    cover_image_title = models.CharField(max_length=200, blank=True)
    banner_image = models.ImageField(upload_to=get_post_upload_path, blank=True)
    banner_image_alt = models.CharField(max_length=200, blank=True)
    banner_image_title = models.CharField(max_length=200, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    time_to_read = models.CharField(max_length=3, blank=True)
    template = models.IntegerField(choices=TEMPLATES, default=0)
    short_description = models.TextField(default='')
    hashtags = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Bejegyzés'
        verbose_name_plural = 'Bejegyzések'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
        convert()

    def get_absolute_url(self):
        return '/blog/%s/' % self.slug


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images', default=None)
    image = models.ImageField(upload_to=get_upload_path)
    url = models.CharField(max_length=200, blank=True)
    url_title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    alt = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ('post',)
        verbose_name = 'Kép'
        verbose_name_plural = 'Képek'

    def __str__(self):
        return self.post.title + " Img"
