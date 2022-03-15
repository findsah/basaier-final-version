
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('basaier.urls')),
    path('news', include('basaier.urls')),
    path('volunteer', include('basaier.urls')),
    path('happystories', include('basaier.urls')),
    path('iqalculator', include('basaier.urls')),
    path('donatedonation', include('basaier.urls')),
    path('seasonalprojects', include('basaier.urls')),
    path('joinchat', include('basaier.urls')),
    path('createownproject', include('basaier.urls')),
    path('refundproject', include('basaier.urls')),
    path('bepartner', include('basaier.urls')),
    path('bepartnersave', include('basaier.urls')),
    path('joinfieldvolunteer', include('basaier.urls')),
    path('volunteerandspread', include('basaier.urls')),
    path('contactus', include('basaier.urls')),
    path('ourpartners', include('basaier.urls')),
    path('aboutus', include('basaier.urls')),
    path('donationbasket', include('basaier.urls')),
    path('paynow', include('basaier.urls')),
    path('signin', include('basaier.urls')),
    path('controlboard', include('basaier.urls')),
    path('donatedonation2', include('basaier.urls')),
    path('detailpage', include('basaier.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
