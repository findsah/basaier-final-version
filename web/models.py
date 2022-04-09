from django.db import models


# Create your models here.
class joinChat(models.Model):
    NO = False
    YES = True
    YES_NO_CHOICES = (
        (NO, 'no'),
        (YES, 'yes')
    )
    country = models.CharField(max_length=255, blank=True)
    whatsappPhone = models.CharField(max_length=255, blank=True)
    contactChoice = models.BooleanField(
        default=NO,
        choices=YES_NO_CHOICES)

    def __str__(self):
        return str(self.whatsappPhone)

    class Meta:
        verbose_name = 'Join Chat'
        verbose_name_plural = 'Join Chats'


class carouselImages(models.Model):
    uploadImage = models.ImageField(upload_to='uploads/')

    def __str__(self):
        return str(self.uploadImage)

    class Meta:
        verbose_name_plural = "Carousel Images"


class boardOfDirectories(models.Model):
    image = models.ImageField(upload_to='uploads/', null=False)
    name = models.CharField(max_length=255, null=False)
    post = models.CharField(max_length=255, null=False)
    facebookLink = models.CharField(max_length=255, null=True)
    twitterLink = models.CharField(max_length=255, null=True)
    instagramLink = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Board Of Directories"


class influencerImages(models.Model):
    donorInfluenceImage = models.ImageField(upload_to='uploads/')
    donorInfluenceDetails = models.CharField(max_length=255)

    def __str__(self):
        return self.donorInfluenceDetails

    class Meta:
        verbose_name_plural = "Images Of Influencer"


class testimonials(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/%Y/%m/%d', null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Testimonials"
