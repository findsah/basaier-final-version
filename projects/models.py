# from tinymce import HTMLField
import decimal

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
from web.sms import sendSMS
from news.models import Profile
from django.conf import settings
from datetime import datetime, timedelta


# from django_model_changes import ChangesMixin


class Category(models.Model):
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


class Project(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category)
    suggestedDonation = models.DecimalField(
        max_digits=10, decimal_places=3, default=1.000)
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
    # countryFlag = models.ImageField(upload_to='countryFlags', blank=True, null=True)
    normal_email = models.EmailField(blank=True, null=True)
    order = models.IntegerField(default=0)
    isZakat = models.BooleanField(default=False)
    is_share = models.BooleanField(default=False)
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
    image = models.ImageField(
        upload_to='projects/%Y/%m/%d', blank=True, null=True)

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

    def __str__(self):
        return self.name

    def is_target_amount(self):
        if self.total_amount is None:
            return False
        return True

    def total_funded(self):
        obj = Donate.objects.filter(
            project=self, transaction__status="Approved").aggregate(total_amount=Sum('amount'))
        if obj['total_amount'] is None:
            return decimal.Decimal('0.000')

        return obj['total_amount']

    def total_efunded(self):
        obj = Donate.objects.filter(project=self,
                                    transaction__status="Approved",
                                    transaction__payment_method__in=["Knet", "KNET", "CreditCard"]) \
            .aggregate(total_amount=Sum('amount'), total_count=Count('id'))
        if obj['total_amount'] is None:
            return decimal.Decimal('0.000')

        return obj['total_amount']

    def total_efunded_per_category(self):
        donates = Donate.objects.values('category__name').filter(
            project=self, transaction__status="Approved",
            transaction__payment_method__in=["Knet", "KNET", "CreditCard"]) \
            .annotate(total_amount=Sum('amount')).order_by()
        donates_per_category = ""
        for index, donate in enumerate(donates):
            if index != 0:
                donates_per_category = donates_per_category + "، "

            donates_per_category = " " + \
                                   donates_per_category + \
                                   donate['category__name'] + ": " + \
                                   str(donate['total_amount'])

        return donates_per_category

    def fund_percent(self):
        if self.total_amount is not None:
            return round((self.total_funded() / self.total_amount) * 100)
        return 0.000

    def number_of_doaat(self):
        return int(self.total_funded() / 300)

    def number_of_students(self):
        return int(self.total_funded() / 45)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ""

    def has_reached_target(self):
        if not self.is_target_amount():
            return False
        return self.total_funded() >= self.total_amount

    def update_close_status(self):
        self.is_closed = self.has_reached_target()
        self.save()

    def remaining(self):
        if self.total_amount is not None:
            return self.total_amount - self.total_funded()
        else:
            return None

    def remaining_percent(self):
        if self.total_amount is not None:
            return round((self.remaining() / self.total_amount) * 100)
        return 0.000

    def get_responsive_image_url(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT")
        if user_agent is None:
            return self.get_image_url()
        if request.user_agent.is_mobile:
            return self.get_image_url()
        return self.get_image_url()

    class Meta:
        verbose_name_plural = "Projects"


@receiver(post_save, sender=Project)
def send_mail_when_project_created_by_admin(sender, instance, **kwargs):
    # WE WILL CREATE THE ARRAY OF recievers, BECAUSE send_email FUNCTION ACCEPTS THE ARRAY OF RECEIVER's EMAILS:
    recievers = []
    recieversMblNumbers = []
    adminMail = settings.EMAIL_HOST_USER
    projectData = Project.objects.order_by('-id')[:1]
    for deptMails in projectData:
        if deptMails.projects_dep_email is not None:
            recievers.append(deptMails.projects_dep_email)
            send_mail('From Basaier', 'Project Created', adminMail, recievers)
        elif deptMails.normal_email is not None:
            recievers.append(deptMails.normal_email)
            send_mail('From Basaier', 'Project Created', adminMail, recievers)
    # message = 'The Project Has Been Created.'
    # fromm = '+96590900055'
    # to = recieversMblNumbers
    # sendSMS(message, fromm, to)


class PostImage(models.Model):
    post = models.ForeignKey(Project, default=None, on_delete=models.CASCADE)
    image = models.FileField(upload_to='projects/%Y/%m/%d')

    def __str__(self):
        return self.post.name


class ProjectPDF(models.Model):
    projectCategory = models.ManyToManyField(Project)
    image = models.ImageField(upload_to='pdfImages', blank=True, null=True)
    file = models.FileField(upload_to='pdfFiles', blank=True, null=True)

    class Meta:
        verbose_name = "PDF File"
        verbose_name_plural = "PDF Files"



class Country(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_en = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.name_en
        else:
            return self.name


class Sacrifice(models.Model):
    choices = (('Sheep', 'Sheep'),
               ('Camel', 'Camel'),
               ('Cow', 'Cow'),
               ('Goat', 'Goat'),
               )

    choices_ar = {'Sheep': 'خروف',
                  'Camel': 'جمل',
                  'Cow': 'بقرة',
                  'Goat': 'ماعز'}

    kind = models.CharField(max_length=50, choices=choices)
    availability = models.IntegerField(default=0)
    country = models.ForeignKey(
        Country, blank=True, null=True, on_delete=models.CASCADE,
        related_name='country')
    project = models.ForeignKey(
        Project, blank=True, null=True, on_delete=models.CASCADE,
        related_name='project')
    price = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)

    # def __str__(self):
    #     if django.utils.translation.get_language() == 'en':
    #         return self.country.get_name()+" - "+self.kind+" - "+str(self.price)+" KWD"
    #     else:
    #         return self.country.get_name()+" - "+ self.choices_ar[self.kind]+" - "+str(self.price)+" KWD"

    def get_name(self):
        if django.utils.translation.get_language() == 'en':
            return self.country.get_name() + " - " + self.kind + " - " + str(self.price) + " KWD"
        else:
            return self.country.get_name() + " - " + self.choices_ar[self.kind] + " - " + str(self.price) + " KWD"


class Transaction(models.Model):
    choices = (('Pending', 'Pending'),
               ('Approved', 'Approved'),
               ('Rejected', 'Rejected'),
               ('Void', 'Void')
               )
    methods = (('Knet', 'Knet'),
               ('Knet_machine', 'Knet_machine'),
               ('CreditCard', 'Credit Card'),
               ('Cash', 'Cash')
               )
    result_choices = (
        ('CAPTURED', 'Captured'),
        ('NOT CAPTURED', 'Not Captured'),
        ('HOST TIMEOUT', 'Host Timeout'),
        ('DENIED BY RISK', 'Denied By Risk'),
        ('CANCELED', 'Cancelled'),
        ('VOIDED', 'Voided')
    )
    status = models.CharField(max_length=10, choices=choices)
    payment_method = models.CharField(
        max_length=20, choices=methods, default='Knet')
    knet_payment_id = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(
        max_length=20, choices=result_choices, blank=True, null=True)
    auth_code = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    trans_id = models.CharField(max_length=255, blank=True, null=True)
    post_date = models.CharField(max_length=255, blank=True, null=True)
    successIndicator = models.CharField(max_length=255, blank=True, null=True)
    tap_id = models.CharField(max_length=255, blank=True, null=True)
    is_tap_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_method

    def total_donation(self):
        donations = Donate.objects.filter(
            transaction=self)
        total_funded = decimal.Decimal('0.000')
        for d in donations:
            total_funded += d.amount
        return total_funded

    class Meta:
        verbose_name_plural = "Transactions"


class TransactionKNETMachine(Transaction):
    class Meta:
        proxy = True
        verbose_name_plural = "TransactionKNETMachine"


class TransactionCash(Transaction):
    class Meta:
        proxy = True
        verbose_name_plural = "Cash Transaction"


class sponsorship(models.Model):
    category = models.CharField(max_length=255)
    categoryEn = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = "Sponsorship Categories"


class sponsorshipProjects(models.Model):
    NO = False
    YES = True
    YES_NO_CHOICES = (
        (NO, 'no'),
        (YES, 'yes')
    )
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
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
    DURATION_CHOICES = (
        (3, 3),
        (6, 6),
        (9, 9),
        (12, 12),
    )
    gender = models.CharField(max_length=11, choices=GENDER_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=3)
    email = models.EmailField(null=True)
    address = models.TextField(null=True)
    category = models.ManyToManyField(sponsorship)
    location = models.CharField(max_length=255, choices=COUNTRY_CHOICES)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)
    is_defined = models.BooleanField(default=False)
    defined_amount = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_hidden = models.BooleanField(
        default=NO,
        choices=YES_NO_CHOICES)
    suggestedDonation = models.DecimalField(
        max_digits=10, decimal_places=3, default=1.000)
    # image = models.ImageField(upload_to='sponsorships/')
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="sponsorship/", null=True)
    default_pic_mapping = {'Male': '00.png', 'Female': '01.png', 'Other': '00.png'}

    def handle(self, *args, **options):
        sponsorshipProjects.objects.filter(created_at__lte=datetime.now() - timedelta(days=365)).delete()
        adminMail = settings.EMAIL_HOST_USER
        send_mail('Sponsorship Project Deleted', 'Sponsorship Project Which Was Created One Year Ago Has Been Deleted',
                  adminMail, [adminMail, ])

    def get_name(self):
        return self.name

    def get_profile_pic_url(self):
        if not self.image:
            return static('media/sponsorships/{}'.format(self.default_pic_mapping[self.gender]))
        return self.image.url

    def __str__(self):
        return self.name

    def is_target_amount2(self):
        if self.total_amount is None:
            return False
        return True

    def total_funded2(self):
        obj = Donate.objects.filter(
            project=self, transaction__status="Approved").aggregate(total_amount=Sum('amount'))
        if obj['total_amount'] is None:
            return decimal.Decimal('0.000')

        return obj['total_amount']

    def total_efunded2(self):
        obj = Donate.objects.filter(project=self,
                                    transaction__status="Approved",
                                    transaction__payment_method__in=["Knet", "KNET", "CreditCard"]) \
            .aggregate(total_amount=Sum('amount'), total_count=Count('id'))
        if obj['total_amount'] is None:
            return decimal.Decimal('0.000')

        return obj['total_amount']

    def total_efunded_per_category2(self):
        donates = Donate.objects.values('category__category').filter(
            project=self, transaction__status="Approved",
            transaction__payment_method__in=["Knet", "KNET", "CreditCard"]) \
            .annotate(total_amount=Sum('amount')).order_by()
        donates_per_category = ""
        for index, donate in enumerate(donates):
            if index != 0:
                donates_per_category = donates_per_category + "، "

            donates_per_category = " " + \
                                   donates_per_category + \
                                   donate['category__category'] + ": " + \
                                   str(donate['total_amount'])
        return donates_per_category

    def fund_percent2(self):
        if self.total_amount is not None:
            return round((self.total_funded2() / self.total_amount) * 100)
        return 0.000

    def has_reached_target2(self):
        if not self.is_target_amount2():
            return False
        return self.total_funded2() >= self.total_amount

    def update_close_status2(self):
        self.is_closed = self.has_reached_target2()
        self.save()

    def remaining2(self):
        if self.total_amount is not None:
            return self.total_amount - self.total_funded2()
        else:
            return None

    class Meta:
        verbose_name_plural = "Sponsorship Projects"


@receiver(post_save, sender=sponsorshipProjects)
def send_mail_when_project_created_by_admin2(sender, instance, **kwargs):
    # WE WILL CREATE THE ARRAY OF recievers, BECAUSE send_email FUNCTION ACCEPTS THE ARRAY OF RECEIVER's EMAILS:
    recievers = []
    recieversMblNumbers = []
    adminMail = settings.EMAIL_HOST_USER
    projectData = sponsorshipProjects.objects.order_by('-id')[:1]
    for mails in projectData:
        if mails.email is not None:
            recievers.append(mails.email)
            send_mail('From Basaier', 'Sponsorship Project Created', adminMail, recievers)
    # message = 'The Project Has Been Created.'
    # fromm = '+96590900055'
    # to = recieversMblNumbers
    # sendSMS(message, fromm, to)


class Donate(models.Model):
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    email = models.CharField(max_length=200, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='donations')
    transaction = models.ForeignKey(
        Transaction, blank=True, null=True, on_delete=models.CASCADE,
        related_name='transaction')
    category = models.ForeignKey(Category, blank=True, null=True,
                                 on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    normal_email = models.EmailField(blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    sacrifice = models.ForeignKey(Sacrifice, blank=True, null=True, on_delete=models.CASCADE,
                                  related_name='sacrifice')
    description = models.CharField(max_length=255, blank=True, null=True)
    recieverPhone = models.CharField(max_length=255, null=True)

    def __str__(self):
        if self.email is not None:
            return self.email
        return self.project.name

    def status(self):
        return self.transaction.status

    def project_name(self):
        if self.category is not None:
            return self.project.name + ": " + self.category.name
        return self.project.name

    def project_donater_name(self):
        if self.project.donater_name is not None:
            return self.project.donater_name
        return ""

    def project_donater_phone(self):
        if self.project.donater_phone is not None:
            return self.project.donater_phone
        return ""

    def payment_method(self):
        return self.transaction.payment_method

    def transaction_id(self):
        return self.transaction.id

    def get_sacrifice_name(self):
        if self.sacrifice is not None:
            if django.utils.translation.get_language() == 'en':
                return self.sacrifice.country.get_name() + " - " + self.sacrifice.kind + " - " + str(
                    self.sacrifice.price) + " KWD"
            else:
                return self.sacrifice.country.get_name() + " - " + self.sacrifice.choices_ar[
                    self.sacrifice.kind] + " - " + str(self.sacrifice.price) + " KWD"

        return ""

    class Meta:
        verbose_name_plural = "Donate"


class DonateSponsor(models.Model):
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    email = models.CharField(max_length=200, blank=True, null=True)
    project = models.ForeignKey(sponsorshipProjects, on_delete=models.CASCADE,
                                related_name='donation', default=None)
    transaction = models.ForeignKey(
        Transaction, blank=True, null=True, on_delete=models.CASCADE,
        related_name='transactions')
    sponsorCategory = models.ForeignKey(sponsorship, blank=True, null=True,
                                        on_delete=models.CASCADE)
    sponsorProject = models.ForeignKey(sponsorshipProjects, blank=True, null=True,
                                       on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    normal_email = models.EmailField(blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    sacrifice = models.ForeignKey(Sacrifice, blank=True, null=True, on_delete=models.CASCADE,
                                  related_name='sacrifices')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.email is not None:
            return self.email
        return self.sponsorProject.name

    def status2(self):
        return self.transaction.status

    def project_name2(self):
        if self.sponsorCategory is not None:
            return self.sponsorProject.name + ": " + self.sponsorCategory.category
        return self.sponsorProject.name

    # def project_donater_name(self):
    #     if self.sponsorProject.donater_name is not None:
    #         return self.sponsorProject.donater_name
    #     return ""
    #
    # def project_donater_phone(self):
    #     if self.sponsorProject.donater_phone is not None:
    #         return self.sponsorProject.donater_phone
    #     return ""

    def payment_method2(self):
        return self.transaction.payment_method

    def transaction_id2(self):
        return self.transaction.id

    def get_sacrifice_name2(self):
        if self.sacrifice is not None:
            if django.utils.translation.get_language() == 'en':
                return self.sacrifice.country.get_name() + " - " + self.sacrifice.kind + " - " + str(
                    self.sacrifice.price) + " KWD"
            else:
                return self.sacrifice.country.get_name() + " - " + self.sacrifice.choices_ar[
                    self.sacrifice.kind] + " - " + str(self.sacrifice.price) + " KWD"

        return ""

    class Meta:
        verbose_name_plural = "Sponsor Donate"


class ProjectsDirectory(models.Model):
    title = models.CharField(max_length=255, blank=True)
    titleEn = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project Directories"

    def __str__(self):
        return self.title

    def get_title(self):
        if django.utils.translation.get_language() == 'en':
            return self.titleEn
        else:
            return self.title


class SMS(models.Model):
    transaction = models.ForeignKey(
        Transaction, blank=True, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SMS"

    def __str__(self):
        return self.phone


class sponsorshipPageContent(models.Model):
    category = models.ManyToManyField(sponsorship)
    firstParagraphIntroduction = models.TextField()

    def __str__(self):
        return self.firstParagraphIntroduction

    class Meta:
        verbose_name_plural = "Sponsorship Page Content"


# class giftCategories(models.Model):
#     name = models.CharField(max_length=255)
#     nameEn = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = "Gift Categories"
#
#
# class gifts(models.Model):
#     name = models.CharField(max_length=255, null=False, blank=False, default=None)
#     nameEn = models.CharField(max_length=255, null=False, blank=False, default=None)
#     image = models.ImageField(upload_to='gifts', null=True, blank=True)
#     price = models.DecimalField(default=0, null=False, max_digits=20, decimal_places=0)
#     category = models.ManyToManyField(giftCategories)
#     details = models.TextField(default=None, null=False, blank=False)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = "Gifts"


class CompaignCategory(models.Model):
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
    is_private = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    nameEn = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=255, null=False, blank=False, choices=COUNTRY_CHOICES, default='Kuwait')
    detail = models.TextField(null=True, blank=True)
    detailEn = models.TextField(null=True, blank=True)
    cost = models.DecimalField(max_digits=100, decimal_places=3, blank=False, null=False)

    # projectsLimit = models.BigIntegerField(null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Compaign Categories"


class Compaigns(models.Model):
    nameOfDeceased = models.CharField(max_length=100, null=False, blank=False)
    nameOfDeceasedEn = models.CharField(max_length=100, null=False, blank=False)
    projectName = models.CharField(max_length=255, null=False, blank=False)
    projectNameEn = models.CharField(max_length=255, null=False, blank=False)
    phone = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='projects/compaigns/%Y/%m/%d', blank=True, null=True)
    is_compaign = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    detail = models.TextField(blank=True, null=True)
    detailEn = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # category = models.ManyToManyField(Category)
    suggestedDonation = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.000)
    compaignCategory = models.ManyToManyField(CompaignCategory)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nameOfDeceased

    class Meta:
        verbose_name_plural = "Compaigns"


class Notifications(models.Model):
    compaignId = models.ForeignKey(Compaigns, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Notifications"


@receiver(post_save, sender=Compaigns)
def whenCompaignCreatedThenUpdateNotificationModel(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(compaignId=instance)


def checkRemainingProjectLimit(categoryId):
    compaignCategoryData = CompaignCategory.objects.filter(id=categoryId)
    for data in compaignCategoryData:
        projectLimit = data.projectsLimit
        # print('LIMIT OF PROJECTS OF CURRENT CATEGORY: ', projectLimit)
    compaignData = Compaigns.objects.filter(compaignCategory=categoryId)
    countedCompaignData = compaignData.count()
    totalRemaining = projectLimit - countedCompaignData
    return totalRemaining
    # print('COUNTED COMPAIGN DATA: ', countedCompaignData)


class CustomerIds(models.Model):
    object_customer = models.CharField(max_length=255, null=True)
    live_mode = models.BooleanField(default=False)
    api_version = models.CharField(max_length=255, null=True)
    customer_id = models.CharField(max_length=255, null=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=False)
    phone = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255)
    currency = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name_plural = "Customer Ids"


class volunteer(models.Model):
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    currentJob = models.CharField(max_length=255, null=True)
    phoneNumber = models.CharField(max_length=255, null=True)
    highestQualification = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Volunteers"


class partner(models.Model):
    organizationName = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    domainOfWork = models.CharField(max_length=255, null=True)
    website = models.CharField(max_length=255, null=True)
    phoneNumber = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)

    def __str__(self):
        return self.organizationName

    class Meta:
        verbose_name_plural = "Partners"
