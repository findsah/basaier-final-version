from django.contrib import admin
from .models import PRCategory, ScienceCategory, PRNews, ScienceNews, Slider, Profile


admin.site.register(PRCategory)
admin.site.register(ScienceCategory)
admin.site.register(PRNews)
admin.site.register(ScienceNews)
admin.site.register(Slider)
admin.site.register(Profile)
