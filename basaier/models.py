from asyncio.windows_events import NULL
import decimal
from unicodedata import name

import django
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import trans_real as trans
from django.templatetags.static import static
# from sendsms.message import SmsMessage
# from web.sms import sendSMS
# from news.models import Profile
from django.conf import settings
from datetime import datetime, timedelta

# Create your models here.

# class signin(models.Model):
#     name = models.CharField(max_length = 150)
#     password = models.CharField(max_length = 150)
#     phone_number = models.CharField(max_length=11)


# class signup(User):
#     mobilenumber = models.CharField(max_length = 150);

class demo(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

class image(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='uploads/')
    
    

class Category(models.Model): # Projects Categories
    name = models.CharField(max_length=100)
    nameEn = models.CharField(max_length=100)
    order = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', related_name='children',
        blank=True, null=True, on_delete=models.CASCADE)
    inMenu = models.BooleanField(default=False)
    inHomePage = models.BooleanField(default=False)
    is_hide = models.BooleanField(default=False)
    is_compaign = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)

    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.nameEn
        else:
            return self.name

    def __str__(self):
        return self.name

    @property
    def total_project(self):
        return Project.objects.filter(category=self).count()

    class Meta:
        verbose_name_plural = "Project Categories"

    def has_children(self):
        return self.children.filter(inMenu=True).exists()

    def all_children(self):
        return Category.objects.exclude(parent=None)

    def children_objects(self):
        return self.children.filter(inMenu=True)
    


class Project(models.Model): # Projects Main  
    NO = False
    YES = True
    YES_NO_CHOICES = (
        (NO, 'no'),
        (YES, 'yes')
    )
    
    slug = models.SlugField(max_length=40, blank=True, null=True)
    name = models.CharField(max_length=100)
    nameEn = models.CharField(max_length=100)
    detail = models.TextField(blank=True, null=True)
    detailEn = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)
    is_defined = models.BooleanField(default=False)
    defined_amount = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_hidden = models.BooleanField(
        default=NO,
        choices=YES_NO_CHOICES)
    deduction = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='projects/%Y/%m/%d', blank=True, null=True)
    image_small = models.ImageField(
        upload_to='projects_small/%Y/%m/%d', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category)
    suggestedDonation = models.DecimalField(
        max_digits=10, decimal_places=3, default=1.000)
    files = models.FileField(upload_to="pdfs/%Y/%m/%d",null=True,blank=True)
    COUNTRY_CHOICES = (
        ("Kuwait", "Kuwait"),
        ("Afghanistan", "Afghanistan"),
        ("Albania", "Albania"),
        ("Algeria", "Algeria"),
        ("Algeria", "Algeria"),
        ("Algeria", "Algeria"),
        ("Antigua and Barbuda", "Antigua and Barbuda"),
        ("Argentina", "Argentina"),
        ("Armenia", "Armenia"),
        ("Australia", "Australia"),
        ("Austria", "Austria"),
        ("Azerbaijan", "Azerbaijan"),
        ("Bahamas", "Bahamas"),
        ("Bahrain", "Bahrain"),
        ("Bangladesh", "Bangladesh"),
        ("Barbados", "Barbados"),
        ("Belarus", "Belarus"),
        ("Belgium", "Belgium"),
        ("Belize", "Belize"),
        ("Benin", "Benin"),
        ("Bhutan", "Bhutan"),
        ("Bolivia", "Bolivia"),
        ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
        ("Botswana", "Botswana"),
        ("Brazil", "Brazil"),
        ("Brunei", "Brunei"),
        ("Bulgaria", "Bulgaria"),
        ("Burkina Faso", "Burkina Faso"),
        ("Burundi", "Burundi"),
        ("Cambodia", "Cambodia"),
        ("Cameroon", "Cameroon"),
        ("Canada", "Canada"),
        ("Cape Verde", "Cape Verde"),
        ("Central African Republic", "Central African Republic"),
        ("Chad", "Chad"),
        ("Chile", "Chile"),
        ("China", "China"),
        ("Colombi", "Colombi"),
        ("Comoros", "Comoros"),
        ("Congo (Brazzaville)", "Congo (Brazzaville)"),
        ("Congo", "Congo"),
        ("Costa Rica", "Costa Rica"),
        ("Cote d'Ivoire", "Cote d'Ivoire"),
        ("Croatia", "Croatia"),
        ("Cuba", "Cuba"),
        ("Cyprus", "Cyprus"),
        ("Czech Republic", "Czech Republic"),
        ("Denmark", "Denmark"),
        ("Djibouti", "Djibouti"),
        ("Dominica", "Dominica"),
        ("Dominican Republic", "Dominican Republic"),
        ("East Timor (Timor Timur)", "East Timor (Timor Timur)"),
        ("Ecuador", "Ecuador"),
        ("Egypt", "Egypt"),
        ("El Salvador", "El Salvador"),
        ("Equatorial Guinea", "Equatorial Guinea"),
        ("Eritrea", "Eritrea"),
        ("Estonia", "Estonia"),
        ("Ethiopia", "Ethiopia"),
        ("Fiji", "Fiji"),
        ("Finland", "Finland"),
        ("France", "France"),
        ("Gabon", "Gabon"),
        ("Gambia, The", "Gambia, The"),
        ("Georgia", "Georgia"),
        ("Germany", "Germany"),
        ("Ghana", "Ghana"),
        ("Greece", "Greece"),
        ("Grenada", "Grenada"),
        ("Guatemala", "Guatemala"),
        ("Guinea", "Guinea"),
        ("Guinea-Bissau", "Guinea-Bissau"),
        ("Guyana", "Guyana"),
        ("Haiti", "Haiti"),
        ("Honduras", "Honduras"),
        ("Hungary", "Hungary"),
        ("Iceland", "Iceland"),
        ("India", "India"),
        ("Indonesia", "Indonesia"),
        ("Iran", "Iran"),
        ("Iraq", "Iraq"),
        ("Ireland", "Ireland"),
        ("Israel", "Israel"),
        ("Italy", "Italy"),
        ("Jamaica", "Jamaica"),
        ("Japan", "Japan"),
        ("Jordan", "Jordan"),
        ("Kazakhstan", "Kazakhstan"),
        ("Kenya", "Kenya"),
        ("Kiribati", "Kiribati"),
        ("Korea, North", "Korea, North"),
        ("Korea, South", "Korea, South"),
        ("Kyrgyzstan", "Kyrgyzstan"),
        ("Laos", "Laos"),
        ("Latvia", "Latvia"),
        ("Lebanon", "Lebanon"),
        ("Lesotho", "Lesotho"),
        ("Liberia", "Liberia"),
        ("Libya", "Libya"),
        ("Liechtenstein", "Liechtenstein"),
        ("Lithuania", "Lithuania"),
        ("Luxembourg", "Luxembourg"),
        ("Macedonia", "Macedonia"),
        ("Madagascar", "Madagascar"),
        ("Malawi", "Malawi"),
        ("Malaysia", "Malaysia"),
        ("Maldives", "Maldives"),
        ("Mali", "Mali"),
        ("Malta", "Malta"),
        ("Marshall Islands", "Marshall Islands"),
        ("Mauritania", "Mauritania"),
        ("Mauritius", "Mauritius"),
        ("Mexico", "Mexico"),
        ("Micronesia", "Micronesia"),
        ("Moldova", "Moldova"),
        ("Monaco", "Monaco"),
        ("Mongolia", "Mongolia"),
        ("Morocco", "Morocco"),
        ("Mozambique", "Mozambique"),
        ("Myanmar", "Myanmar"),
        ("Namibia", "Namibia"),
        ("Nauru", "Nauru"),
        ("Nepa", "Nepa"),
        ("Netherlands", "Netherlands"),
        ("New Zealand", "New Zealand"),
        ("Nicaragua", "Nicaragua"),
        ("Niger", "Niger"),
        ("Nigeria", "Nigeria"),
        ("Norway", "Norway"),
        ("Oman", "Oman"),
        ("Pakistan", "Pakistan"),
        ("Palau", "Palau"),
        ("Panama", "Panama"),
        ("Papua New Guinea", "Papua New Guinea"),
        ("Paraguay", "Paraguay"),
        ("Peru", "Peru"),
        ("Philippines", "Philippines"),
        ("Poland", "Poland"),
        ("Portugal", "Portugal"),
        ("Qatar", "Qatar"),
        ("Romania", "Romania"),
        ("Russia", "Russia"),
        ("Rwanda", "Rwanda"),
        ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
        ("Saint Lucia", "Saint Lucia"),
        ("Saint Vincent", "Saint Vincent"),
        ("Samoa", "Samoa"),
        ("San Marino", "San Marino"),
        ("Sao Tome and Principe", "Sao Tome and Principe"),
        ("Saudi Arabia", "Saudi Arabia"),
        ("Senegal", "Senegal"),
        ("Serbia and Montenegro", "Serbia and Montenegro"),
        ("Seychelles", "Seychelles"),
        ("Sierra Leone", "Sierra Leone"),
        ("Singapore", "Singapore"),
        ("Slovakia", "Slovakia"),
        ("Slovenia", "Slovenia"),
        ("Solomon Islands", "Solomon Islands"),
        ("Somalia", "Somalia"),
        ("South Africa", "South Africa"),
        ("Spain", "Spain"),
        ("Sri Lanka", "Sri Lanka"),
        ("Sudan", "Sudan"),
        ("Suriname", "Suriname"),
        ("Swaziland", "Swaziland"),
        ("Sweden", "Sweden"),
        ("Switzerland", "Switzerland"),
        ("Syria", "Syria"),
        ("Taiwan", "Taiwan"),
        ("Tajikistan", "Tajikistan"),
        ("Tanzania", "Tanzania"),
        ("Thailand", "Thailand"),
        ("Togo", "Togo"),
        ("Tonga", "Tonga"),
        ("Trinidad and Tobago", "Trinidad and Tobago"),
        ("Tunisia", "Tunisia"),
        ("Turkey", "Turkey"),
        ("Turkmenistan", "Turkmenistan"),
        ("Tuvalu", "Tuvalu"),
        ("Uganda", "Uganda"),
        ("Ukraine", "Ukraine"),
        ("United Arab Emirates", "United Arab Emirates"),
        ("United Kingdom", "United Kingdom"),
        ("United States", "United States"),
        ("Uruguay", "Uruguay"),
        ("Uzbekistan", "Uzbekistan"),
        ("Vanuatu", "Vanuatu"),
        ("Vatican City", "Vatican City"),
        ("Venezuela", "Venezuela"),
        ("Vietnam", "Vietnam"),
        ("Yemen", "Yemen"),
        ("Zambia", "Zambia"),
        ("Zimbabwe", "Zimbabwe")
    )
    
    location = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=False, default='Kuwait')
    countryFlag = models.ImageField(upload_to='countryFlags', blank=True, null=True)
    normal_email = models.EmailField(blank=True, null=True)
    order = models.IntegerField(default=0)
    isZakat = models.BooleanField(default=False)
    isGift = models.BooleanField(default=False)
    is_share = models.BooleanField(default=False) # removed
    is_thawab = models.BooleanField(default=False)
    is_compaign = models.BooleanField(default=False)
    active_compaign = models.BooleanField(default=False)
    is_sadaqah = models.BooleanField(default=False)
    share_jump = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    projects_dep_email = models.CharField(max_length=255, blank=True, null=True)
    finaince_dep_email = models.CharField(max_length=255, blank=True, null=True)
    donater_name = models.CharField(max_length=255, blank=True, null=True)
    donater_phone = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.IntegerField(null=True)
    
    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.nameEn
        else:
            return self.name

    def get_detail(self):
        if django.utils.translation.get_language() == 'en':
            return self.detailEn
        else:
            return self.detail
    def get_category(self):
        return "\n".join([p.name for p in self.category.all()])
     
    

    
    
    

    
       
