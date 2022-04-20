import django
from django.db import models
# from tinymce import models.TextField
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = "Profiles"


class PRCategory(models.Model):
    name = models.CharField(max_length=100)
    nameEn = models.CharField(max_length=100)
    order = models.IntegerField()
    parent = models.ForeignKey(
        'self', related_name='children',
        blank=True, null=True, on_delete=models.DO_NOTHING)

    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.nameEn
        else:
            return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "PR Categories"

    @property
    def total_news(self):
        return PRNews.objects.filter(category=self).count()


class ScienceCategory(models.Model):
    name = models.CharField(max_length=100)
    nameEn = models.CharField(max_length=100)
    order = models.IntegerField()
    parent = models.ForeignKey(
        'self', related_name='children',
        blank=True, null=True, on_delete=models.DO_NOTHING)

    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.nameEn
        else:
            return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Science Categories"

    @property
    def total_news(self):
        return ScienceNews.objects.filter(category=self).count()


class PRNews(models.Model):
    title = models.CharField(max_length=200)
    titleEn = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    contentEn = models.TextField(blank=True)
    category = models.ForeignKey(PRCategory, on_delete=models.DO_NOTHING)
    image = models.FileField(upload_to='news/%Y/%m/%d', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video = models.FileField(upload_to='news/videos/%Y/%m/%d', blank=True, null=True)

    class Meta:
        verbose_name_plural = "PR News"

    def get_title(self):
        if django.utils.translation.get_language() == 'en':
            return self.titleEn
        else:
            return self.title

    def get_content(self):
        if django.utils.translation.get_language() == 'en':
            return self.contentEn
        else:
            return self.content

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ""


class ScienceNews(models.Model):
    title = models.CharField(max_length=200)
    titleEn = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    contentEn = models.TextField(blank=True)
    category = models.ForeignKey(ScienceCategory, on_delete=models.DO_NOTHING)
    image = models.FileField(upload_to='stories/%Y/%m/%d', blank=True, null=True)
    video = models.FileField(upload_to='stories/videos/%Y/%m/%d', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # meetingLink = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "Stories"
        verbose_name = "Stories"

    def get_title(self):
        if django.utils.translation.get_language() == 'en':
            return self.titleEn
        else:
            return self.title

    def get_content(self):
        if django.utils.translation.get_language() == 'en':
            return self.contentEn
        else:
            return self.content

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ""


class Slider(models.Model):
    title = models.CharField(max_length=200)
    titleEn = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    contentEn = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='sliders/%Y/%m/%d',
        blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    button_title = models.CharField(max_length=200)
    button_titleEn = models.CharField(max_length=200)
    link = models.URLField(max_length=200, blank=True, null=True)

    def get_title(self):
        if django.utils.translation.get_language() == 'en':
            return self.titleEn
        else:
            return self.title

    def get_content(self):
        if django.utils.translation.get_language() == 'en':
            return self.contentEn
        else:
            return self.content

    def get_button_title(self):
        if django.utils.translation.get_language() == 'en':
            return self.button_titleEn
        else:
            return self.button_title

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ""

    def __str__(self):
        return self.title
