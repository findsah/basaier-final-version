from django.db import models


# Create your models here.
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
