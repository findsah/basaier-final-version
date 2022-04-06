from django.contrib import admin
from .models import carouselImages, boardOfDirectories, influencerImages, joinChat, testimonials


admin.site.register(joinChat)
admin.site.register(carouselImages)
admin.site.register(boardOfDirectories)
admin.site.register(influencerImages)
admin.site.register(testimonials)
