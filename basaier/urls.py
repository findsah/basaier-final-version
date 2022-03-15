
from django.urls import path,re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('', views.index, name="index"),
    path('news', views.news, name="news"),
    path('volunteer', views.volunteer, name="volunteer"),
    path('happystories', views.happystories, name="happystories"),
    path('iqalculator', views.iqalculator, name="iqalculator"),
    path('donatedonation', views.donatedonation, name="donatedonation"),
    path('seasonalprojects', views.seasonalprojects, name="seasonalprojects"),
    path('search_project',views.search_project, name='searchproject'),
    path('joinchat', views.joinchat, name="joinchat"),
    path('createownproject', views.createownproject, name="createownproject"),
    path('refundproject/<int:id>', views.refundproject, name="refundproject"),
    path('upload_pdf/<int:the_id>',views.upload_pdf,name="upload_pdf"),
    re_path(r'download/(?P<path>.*)$',serve,{'document_root' : settings.MEDIA_ROOT}),
    path('bepartner', views.bepartner, name="bepartner"),
    path('bepartnersave', views.bepartnersave, name="bepartnersave"),
    path('joinfieldvolunteer', views.joinfieldvolunteer, name="joinfieldvolunteer"),
    path('volunteerandspread', views.volunteerandspread, name="volunteerandspread"),
    path('contactus', views.contactus, name="contactus"),
    path('ourpartners', views.ourpartners, name="ourpartners"),
    path('aboutus', views.aboutus, name="aboutus"),
    path('donationbasket', views.donationbasket, name="donationbasket"),
    path('paynow', views.paynow, name="paynow"),
    path('demo', views.demo_view, name="demo"),                            
    path('signin', views.signin, name="signin"),
    path('controlboard', views.controlboard, name="controlboard"),
    path('donatedonation2', views.donatedonation2, name="donatedonation2"),
    path('detailpage', views.detailpage, name="detailpage"),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)