import http.client
from datetime import timedelta, datetime

import boto3
import pyrebase
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import activate, to_locale, get_language
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView  # Import TemplateView
from django.views.generic import View
from rest_framework.utils import json
from web.toSendSMS import sendSMS
import random

from libraries import helpers
from news.models import Profile
from news.models import Slider, PRNews, PRCategory, \
    ScienceCategory, ScienceNews
from people.models import Contact
from projects.models import Project, Category, \
    Transaction, Donate, ProjectsDirectory, SMS, Sacrifice, sponsorship, sponsorshipProjects, sponsorshipPageContent, \
    CompaignCategory, Compaigns, CustomerIds, DonateSponsor, volunteer, partner, ProjectPDF, PostImage, \
    giftSenderReceiver, createOwnProjectModel
from web.models import boardOfDirectories, influencerImages, joinChat, testimonials
from .filters import ProjectFilter
from .tokens import account_activation_token

# from web.cart import Cart

config = {
    "apiKey": "553f4037184cf18490885a33458dc1cdce96b642",
    "authDomain": "basaier-8a7fe.firebaseapp.com",
    "databaseURL": "https://basaier-8a7fe.firebaseio.com",
    "storageBucket": "basaier-8a7fe.appspot.com"
}

firebase = pyrebase.initialize_app(config)


def getCurrency(request):
    # myIp = ipapi.location(output='currency')
    # myIp = get_client_ip(request)
    # if request.method == 'POST':
    currencyValue = request.GET.get('getvalueStr')
    print(currencyValue)
    # print(get_language())
    request.session['fetchedCurrencyFromAjax'] = currencyValue
    # print(request.get.session('fetchedCurrencyFromAjax'))
    return HttpResponse('')
    # else:
    #     return 'KWD'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # print "returning FORWARDED_FOR"
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        # print "returning REAL_IP"
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        # print "returning REMOTE_ADDR"
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_credit_card_payment(request, transaction):
    try:
        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        # order = {'currency': getMyCurrency, 'id': transaction.pk}
        order = {'currency': 'KWD', 'id': transaction.pk}
        payload = {'apiOperation': 'CREATE_CHECKOUT_SESSION', 'order': order}
        data_json = json.dumps(payload)
        print(data_json)

        response = requests.post(
            url=settings.MASTERCARD_URL,
            headers={
                "Content-Type": "application/json",
                "Accept-Charset": "UTF-8",
                "Cache-Control": "no-cache"
            },
            data=data_json,
            auth=(settings.MASTERCARD_USERNAME, settings.MASTERCARD_PASSWORD)
        )

        if response.status_code != 201:
            return None, None

        obj = response.json()
        transaction.successIndicator = obj['successIndicator']
        transaction.save()

        return obj['session']['id'], amount
    except Exception as e:
        print(e)
        return None, None


# Active
class OnlinePaymentTap(TemplateView):
    template_name = "web/response.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated == True:
            userId = request.user.id
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        email = request.POST.get('email', '')
        recieverPhone = request.POST.get('recieverPhone', '')
        project_category_ids = request.POST.getlist(
            'project_category_id[]', '')
        print("PROJECT CATEGORY ID'S: ", project_category_ids)
        sacrifice_id = int(request.POST.get('sacrifice', 0))
        sacrifice = None
        if sacrifice_id > 0:
            sacrifice = Sacrifice.objects.get(pk=sacrifice_id)
        quantity = int(request.POST.get('quantity', 0))
        if sacrifice is not None and not sacrifice.availability >= quantity:
            return redirect(get_domain_url(request) + "/project/" + str(sacrifice.project.id) + "/detail")
        payment_method = request.POST.get('payment_method')
        phones = helpers.remove_dublicates(
            request.POST.getlist('phones[]', ''))
        transaction = Transaction.objects.create(
            status='Pending', payment_method=payment_method, is_tap_payment=True)
        for phone in phones:
            SMS.objects.create(transaction=transaction, phone=phone)
        donates = []
        for i, project_id in enumerate(project_ids):
            # project_remaining = Project.objects.get(id=int(project_ids[i])).remaining()
            # if project_remaining is not None and project_remaining < float(amounts[i]):
            #     sliders = Slider.objects.all().order_by('-id')[:5]
            #     project_dirctories = ProjectsDirectory.objects.all()
            #     projects = Project.objects.filter(
            #         is_closed=False, is_hidden=False, category__inHomePage=True
            #     ).order_by('-id')
            #     news = PRNews.objects.all().order_by('-id')[:6]
            #     science_news = ScienceNews.objects.all().order_by('-id')[:6]
            #     categories = PRCategory.objects.all().order_by('-id')
            #     charity_categories = Category.objects.filter(
            #         inMenu=True, inHomePage=True, parent=None
            #     ).order_by('-id')
            #     cart_projects, projects_selected = get_cart(request)
            #     return render(request, self.template_name,
            #                   {'sliders': sliders,
            #                    'projects': projects,
            #                    'categories': categories,
            #                    'charity_categories': charity_categories,
            #                    'news': news,
            #                    'science_news': science_news,
            #                    'cart_projects': cart_projects,
            #                    'projects_selected': projects_selected,
            #                    'project_dirctories': project_dirctories})
            if request.user.is_authenticated == True:
                userId2 = request.user.id
                userInstance = get_object_or_404(User, id=userId2)
            if request.user.id is not None:
                donate = Donate.objects.create(
                    user=userInstance, amount=amounts[i], email=email, project_id=int(
                        project_ids[i]),
                    transaction=transaction,
                    category_id=int(project_category_ids[i]),
                    recieverPhone=recieverPhone)
            else:
                donate = Donate.objects.create(
                    amount=amounts[i], email=email, project_id=int(
                        project_ids[i]),
                    transaction=transaction,
                    category_id=int(project_category_ids[i]),
                    recieverPhone=recieverPhone)
            donates.append(donate)

        url, reference, transaction = generate_payment_url_tap(
            request, transaction, payment_method)
        return redirect(url)


class OnlineSubscriptionTap(TemplateView):
    template_name = "web/response.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        userId = request.user.id
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        email = request.user.email
        interval = request.POST.get('interval')
        period = request.POST.get('period')
        fromDate = request.POST.get('from')
        auto_renew = request.POST.get('auto_renew')
        timezone = request.POST.get('timezone')
        currency = request.POST.get('currency')
        description = request.POST.get('description', '')
        # project_category_ids = request.POST.getlist('project_category_id[]', '')
        # categoryId = request.POST.getlist('categoryId[]')
        sacrifice_id = int(request.POST.get('sacrifice', 0))
        sacrifice = None
        if sacrifice_id > 0:
            sacrifice = Sacrifice.objects.get(pk=sacrifice_id)
        quantity = int(request.POST.get('quantity', 0))
        if sacrifice is not None and not sacrifice.availability >= quantity:
            return redirect(get_domain_url(request) + "/project/" + str(sacrifice.project.id) + "/detail")
        payment_method = request.POST.get('payment_method')
        project_category_ids = request.POST.getlist(
            'project_category_id[]', '')
        # print("ONLINE_SUBSCRIPTION_TAP: ", project_category_ids)
        phones = helpers.remove_dublicates(
            request.POST.getlist('phones[]', ''))
        transaction = Transaction.objects.create(
            status='Pending', payment_method=payment_method, is_tap_payment=True)
        for phone in phones:
            SMS.objects.create(transaction=transaction, phone=phone)
        donates = []
        for i, project_id in enumerate(project_ids):
            if sacrifice is not None:
                donate = DonateSponsor.objects.create(
                    user=userId, amount=amounts[i], email=email, project_id=int(
                        project_ids[i]),
                    transaction=transaction,
                    sponsorCategory=sponsorship.objects.get(
                        pk=int(project_category_ids[i])),
                    sponsorProject=sponsorshipProjects.objects.get(
                        pk=int(project_ids[i])),
                    qty=quantity,
                    sacrifice=sacrifice,
                    description=sacrifice.get_name())
            else:
                donate = DonateSponsor.objects.create(
                    amount=amounts[i], email=email, project_id=int(
                        project_ids[i]),
                    transaction=transaction,
                    sponsorCategory=sponsorship.objects.get(
                        pk=int(project_category_ids[i])),
                    sponsorProject=sponsorshipProjects.objects.get(
                        pk=int(project_ids[i])))
                donates.append(donate)
                ifCustomerExits = CustomerIds.objects.filter(email=email)
                totalData = ifCustomerExits.count()
                if totalData > 1:
                    for data in ifCustomerExits:
                        customerId = data.customer_id
                    url, reference, transaction = generate_sponsor_payment_url_tap(
                        request, transaction, payment_method, interval, period, fromDate, auto_renew, timezone,
                        currency,
                        description, customerId)
                    return redirect(url)
                else:
                    # CREATE CUSTOMER:
                    createTheCustomer = create_customer_sponsor_url(request)
                    print(createTheCustomer)
                    # for data in createTheCustomer:
                    #     status_code = data.statusCode
                    # if createTheCustomer.status_code == 200:
                    ifCustomerExits = CustomerIds.objects.filter(email=email)
                    totalData = ifCustomerExits.count()
                    if totalData > 1:
                        for data in ifCustomerExits:
                            customerId = data.customer_id
                        url, reference, transaction = generate_sponsor_payment_url_tap(
                            request, transaction, payment_method, interval, period, fromDate, auto_renew, timezone,
                            currency,
                            description, customerId)
                    return redirect(url)


def create_customer_sponsor_url(request):
    if request.user.is_authenticated == True:
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        userInstance = request.user.id
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
        profileData = Profile.objects.filter(user=userInstance)
        for data in profileData:
            phone = data.phone
            print(phone)
        payload = {
            "first_name": first_name,
            "middle_name": "",
            "last_name": last_name,
            "email": email,
            "phone": {
                "country_code": "965",
                "number": "00000000"
            },
            "description": "test",
            "metadata": {
                "udf1": "test"
            },
            "currency": "KWD"
            # "currency": getMyCurrency
        }
        headers = {
            'authorization': "Bearer " + settings.TAP_API_KEY,
            'content-type': "application/json"
        }
        payload = json.dumps(payload)
        response = requests.request(
            "POST", settings.TAP_PAY_CUSTOMER_URL, data=payload, headers=headers)
        print("RESPONSE FROM THE CUSTOMER URL: ", response.status_code)
        json_data = json.loads(response.text)
        # print(json_data)
        statusCode = response.status_code
        object = json_data["object"]
        live_mode = json_data["live_mode"]
        # api_version = json_data["api_version"]
        id = json_data["id"]
        request.session['justCreatedCustomerId'] = json_data["id"]
        first_name = json_data["first_name"]
        last_name = json_data["last_name"]
        email = json_data["email"]
        phone = json_data["phone"]
        description = json_data["description"]
        currency = json_data["currency"]
        # title = json_data["title"]
        # nationality = json_data["nationality"]
        insertInDatabase = CustomerIds.objects.create(
            object_customer=object,
            live_mode=live_mode,
            # api_version=api_version,
            customer_id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            description=description,
            currency=currency,
            # title=title,
            # nationality=nationality,

        )
        return {'statusCode': statusCode, 'id': id}


class OnlinePayment(TemplateView):
    template_name = "web/credit_card.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        email = request.POST.get('email', '')
        payment_method = request.POST.get('payment_method')
        project_category_ids = request.POST.getlist('project_category_id[]')
        phones = helpers.remove_dublicates(request.POST.getlist('phones[]'))
        names = request.POST.get('fullname', '')
        transaction = Transaction.objects.create(
            status='Pending', payment_method=payment_method)
        for x, phone in enumerate(phones):
            SMS.objects.create(transaction=transaction,
                               phone=phone, name=names)
        donates = []
        for i, project_id in enumerate(project_ids):
            donate = Donate.objects.create(
                amount=amounts[i], email=email, project_id=int(project_ids[i]),
                transaction=transaction,
                category_id=int(project_category_ids[i]))
            donates.append(donate)

        if payment_method == 'Knet':
            url, reference, transaction = generate_payment_url(
                request, transaction)
            return redirect(url)

        session_id, amount = generate_credit_card_payment(request, transaction)
        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'donates': donates,
                       'session_id': session_id,
                       'amount': amount,
                       'transaction_id': transaction.id,
                       'merchant': settings.MASTERCARD_MERCHANT
                       })


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessOfCreditCard(View):
    def get(self, request):
        # try:
        payment_id = request.GET.get("resultIndicator")
        print(payment_id)
        transaction = Transaction.objects.filter(
            successIndicator=payment_id)
        transaction = transaction[0]
        transaction.result = 'CAPTURED'
        transaction.status = 'Approved'
        transaction.save()

        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)

        project = donates[0].project
        update_total_fund_firebase(project)

        request.session['amounts'] = []
        request.session['project_ids'] = []
        cart = Cart(request)
        cart.removeAll()

        fetchProjectName = Donate.objects.filter(
            transaction=transaction).order_by('-id')
        for data in fetchProjectName:
            projectIdFetchedFromDonationTable = data.project.id
            print("projectIdFetchedFromDonationTable",
                  projectIdFetchedFromDonationTable)
        try:
            senderReceiverModel = giftSenderReceiver.objects.filter(
                project=projectIdFetchedFromDonationTable).order_by('-id')[0]
            print("DATA IN MODEL:", senderReceiverModel)
            senderReceiverModel.status = 'Approved'
            senderReceiverModel.save()
        except Exception as e:
            pass

        html_message = loader.render_to_string(
            'web/email.html',
            {
                "amount": amount, "reference_id": transaction.successIndicator,
                "payment_id": transaction.successIndicator,
                "db_id": transaction.id,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates
            }
        )
        # try:
        email_subject = 'شكرا لتبرعك مع جمعية بصائر الخيرية'
        to_list = donates[0].email
        adminMail = settings.EMAIL_HOST_USER
        mail = EmailMultiAlternatives(
            email_subject, 'This is message', adminMail, [to_list])
        mail.attach_alternative(html_message, "text/html")
        # except:
        #     pass

        # try:
        mail.send()
        print("MAIL SENT AFTER SUCCESS PAYMENT:")
        # except Exception:
        #     pass

        # TO SEND SMS IF THE DONATION WAS AS GIFT:
        if donates[0].recieverPhone is not None:
            fromSender = 'S@basorg'
            fetchProjectName = Donate.objects.filter(
                transaction=transaction).order_by('-id')
            for data in fetchProjectName:
                nameProject = data.project.name
                request.session['projectName'] = nameProject
            projectName = request.session.get('projectName')
            print("IF DONATED AS GIFT:", projectName)
            phoneNumber = donates[0].recieverPhone
            amount = donates[0].amount
            print("IF DONATED AS GIFT:", phoneNumber)
            message = "تم اهداؤكم تبرع في مشروع {} بقيمة {}".format(
                projectName, amount)
            print(message)
            callThat = sendSMS(message, fromSender, phoneNumber)
            # print(callThat)
            if callThat == 200:
                print("Message Delivered")

        # client = boto3.client(
        #     'sns', settings.AWS_SNS_ZONE,
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        # )
        sms = SMS.objects.filter(transaction=transaction)
        for obj in sms:
            try:
                # phone = phonenumbers.parse(obj.phone, None)
                # if phonenumbers.is_valid_number(phone):
                # paymentId = donates[0].transaction_id
                message = 'تم قبول تبرعكم  بقيمة {} رقم العملية {} شكراً لكم'.format(
                    amount, payment_id)

                fromSender = 'S@basorg'
                callThat = sendSMS(message, fromSender, obj.phone)
                if callThat == 200:
                    print("Invoice Message Sent.", callThat)
            except Exception:
                pass

        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        sponsorCategories = sponsorship.objects.all()

        return render(
            request, "web/checkout_result.html",
            {
                "amount": amount, "reference_id": transaction.successIndicator,
                "payment_id": transaction.successIndicator,
                "db_id": transaction.pk,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates,
                'charity_categories': charity_categories,
                'sponsorCategories': sponsorCategories,
            }
        )
        # except Exception as e:
        #     return redirect('/')


class Index(TemplateView):
    template_name = "web/index2.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                          is_compaign=False, is_thawab=False).order_by('-id')
        projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                                 is_compaign=False).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        news2 = PRNews.objects.all().order_by('-id')[:4]
        testimonialsData = testimonials.objects.all().order_by('-id')[:3]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        # whoWeAreVar = whoWeAre.objects.all()
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'projects': projects,
                       'projectsSadaqah': projectsSadaqah,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'news2': news2,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       # 'whoWeAreVar': whoWeAreVar,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       'testimonialsData': testimonialsData,
                       })


# class ProjectDetail(TemplateView):
#     template_name = "web/project_detail.html"
#
#     def get(self, request, *args, **kwargs):
#         cart = Cart(request)
#         totalProjectsInCart = cart.get_total_products()
#         # getMyCurrency = getCurrency(request)
#         getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#         sliders = Slider.objects.all().order_by('-id')[:5]
#         project_dirctories = ProjectsDirectory.objects.all()
#         project = None
#         if 'slug' in kwargs:
#             project = get_object_or_404(Project, slug=kwargs['slug'])
#         else:
#             project = get_object_or_404(Project, pk=kwargs['id'])
#
#         # if (project.total_amount is not None) and(project.total_amount > 0 and int(project.remaining()) == 0) or project.is_closed:
#         #     return redirect("/")
#
#         categories = PRCategory.objects.all().order_by('-id')
#         sponsorCategories = sponsorship.objects.all()
#         charity_categories = Category.objects.filter(
#             inMenu=True, parent=None).order_by('-id')
#         latest_projects = Project.objects.filter(
#             is_closed=False, is_hidden=False, category__inHomePage=True, is_compaign=False).order_by('-id')[:6]
#         cart_projects, projects_selected = get_cart(request)
#         sacrifices = Sacrifice.objects.filter(availability__gt=0, project=project).order_by('country').all()
#         sacrifices_json_data = Sacrifice.objects.filter(availability__gt=0, project=project).values()
#
#         sacrifices_json = json.dumps(list(sacrifices_json_data), cls=DjangoJSONEncoder)
#         if len(sacrifices_json_data) > 0:
#             self.template_name = "web/project_sacrifice_detail_.html"
#         if request.user.is_authenticated:
#             userId = request.user.id
#             userInstance = get_object_or_404(User, id=userId)
#             profile = get_object_or_404(Profile, user=userInstance)
#             phoneNumberOfUser = profile.phone
#         else:
#             phoneNumberOfUser = ''
#
#         return render(request, self.template_name,
#                       {'sliders': sliders,
#                        'categories': categories,
#                        'charity_categories': charity_categories,
#                        'latest_projects': latest_projects,
#                        'project': project,
#                        'sponsorCategories': sponsorCategories,
#                        'cart_projects': cart_projects,
#                        'projects_selected': projects_selected,
#                        'project_dirctories': project_dirctories,
#                        'sacrifices_json': sacrifices_json,
#                        'sacrifices': sacrifices,
#                        'totalProjectsInCart': totalProjectsInCart,
#                        'getMyCurrency': getMyCurrency,
#                        'phoneNumberOfUser': phoneNumberOfUser,
#                        })
#
#     def post(self, request, *args, **kwargs):
#         cart = Cart(request)
#         totalProjectsInCart = cart.get_total_products()
#         # getMyCurrency = getCurrency(request)
#         getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#         numberOfShare = int(request.POST.get('numberOfShare', 0))
#
#         amounts = request.POST.getlist('amount[]', [""])
#         # print(amounts)
#         # if amounts == [""]:
#         #     amounts = ["0.0"]
#
#         # project_category_ids = request.POST.getlist('project_category_id[]')
#         sliders = Slider.objects.all().order_by('-id')[:5]
#         project_dirctories = ProjectsDirectory.objects.all()
#         project = None
#
#         if 'slug' in kwargs:
#             project = get_object_or_404(Project, slug=kwargs['slug'])
#         else:
#             project = get_object_or_404(Project, pk=kwargs['id'])
#             # fetchProject = Project.objects.values('id', 'category__id').filter(pk=kwargs['id'])
#             # for data in fetchProject:
#             #     print(data)
#         categories = PRCategory.objects.all().order_by('-id')
#         sponsorCategories = sponsorship.objects.all()
#         charity_categories = Category.objects.filter(
#             inMenu=True, parent=None).order_by('-id')
#         latest_projects = Project.objects.filter(
#             is_closed=False, is_hidden=False, category__inHomePage=True, is_compaign=False).order_by('-id')[:6]
#         cart_projects, projects_selected = get_cart(request)
#         sacrifices = Sacrifice.objects.filter(availability__gt=0, project=project).order_by('country').all()
#         sacrifices_json_data = Sacrifice.objects.filter(availability__gt=0, project=project).values()
#         sacrifices_json = json.dumps(list(sacrifices_json_data), cls=DjangoJSONEncoder)
#         if len(sacrifices_json_data) > 0:
#             self.template_name = "web/project_sacrifice_detail_.html"
#         return render(request, self.template_name,
#                       {'sliders': sliders,
#                        'categories': categories,
#                        'charity_categories': charity_categories,
#                        'latest_projects': latest_projects,
#                        'project': project,
#                        'sponsorCategories': sponsorCategories,
#                        'cart_projects': cart_projects,
#                        'projects_selected': projects_selected,
#                        'project_dirctories': project_dirctories,
#                        'numberOfShare': numberOfShare,
#                        'amount': "{0:.3f}".format(float(amounts[0].strip())),
#                        # 'project_category_id': int(project_category_ids[0]),
#                        'sacrifices_json': sacrifices_json,
#                        'sacrifices': sacrifices,
#                        'totalProjectsInCart': totalProjectsInCart,
#                        'getMyCurrency': getMyCurrency,
#                        })


# BASAIER DESIGN HAS BEEN CHANGED, SO WE HAVE USED NEW TEMPLATE FOR DISPLAYING DETAIL OF A PARTICULAR PROJECT.
class ProjectDetail(TemplateView):
    template_name = "web/refundproject.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        project = None
        if 'slug' in kwargs:
            project = get_object_or_404(Project, slug=kwargs['slug'])
        else:
            project = get_object_or_404(Project, pk=kwargs['id'])
        id = kwargs['id']
        # if (project.total_amount is not None) and(project.total_amount > 0 and int(project.remaining()) == 0) or project.is_closed:
        #     return redirect("/")

        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False).order_by('-id')[:6]
        print("PROJECTS ID: 721:", id)
        projects = Project.objects.filter(pk=id)
        pdfFiles = ProjectPDF.objects.filter(projectCategory=id)
        multipleImages = PostImage.objects.filter(post=id)
        for data in multipleImages:
            print(data.image)
        cart_projects, projects_selected = get_cart(request)
        sacrifices = Sacrifice.objects.filter(
            availability__gt=0, project=project).order_by('country').all()
        sacrifices_json_data = Sacrifice.objects.filter(
            availability__gt=0, project=project).values()

        sacrifices_json = json.dumps(
            list(sacrifices_json_data), cls=DjangoJSONEncoder)
        if len(sacrifices_json_data) > 0:
            self.template_name = "web/project_sacrifice_detail_.html"
        # if request.user.is_authenticated:
        #     userId = request.user.id
        #     userInstance = get_object_or_404(User, id=userId)
        #     profile = get_object_or_404(Profile, user=userInstance)
        #     phoneNumberOfUser = profile.phone
        # else:
        #     phoneNumberOfUser = ''

        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'project': project,
                       'projects': projects,
                       'pdfFiles': pdfFiles,
                       'multipleImages': multipleImages,
                       'sponsorCategories': sponsorCategories,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'sacrifices_json': sacrifices_json,
                       'sacrifices': sacrifices,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       # 'phoneNumberOfUser': phoneNumberOfUser,
                       })

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        numberOfShare = int(request.POST.get('numberOfShare', 0))

        amounts = request.POST.getlist('amount[]', [""])
        # print(amounts)
        # if amounts == [""]:
        #     amounts = ["0.0"]

        # project_category_ids = request.POST.getlist('project_category_id[]')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        project = None

        if 'slug' in kwargs:
            project = get_object_or_404(Project, slug=kwargs['slug'])
        else:
            project = get_object_or_404(Project, pk=kwargs['id'])
            # fetchProject = Project.objects.values('id', 'category__id').filter(pk=kwargs['id'])
            # for data in fetchProject:
            #     print(data)
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        sacrifices = Sacrifice.objects.filter(
            availability__gt=0, project=project).order_by('country').all()
        sacrifices_json_data = Sacrifice.objects.filter(
            availability__gt=0, project=project).values()
        sacrifices_json = json.dumps(
            list(sacrifices_json_data), cls=DjangoJSONEncoder)
        if len(sacrifices_json_data) > 0:
            self.template_name = "web/project_sacrifice_detail_.html"
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'project': project,
                       'sponsorCategories': sponsorCategories,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'numberOfShare': numberOfShare,
                       'amount': "{0:.3f}".format(float(amounts[0].strip())),
                       # 'project_category_id': int(project_category_ids[0]),
                       'sacrifices_json': sacrifices_json,
                       'sacrifices': sacrifices,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


class privateProjectDetail(TemplateView):
    template_name = "web/refundproject.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        project = None
        if 'slug' in kwargs:
            project = get_object_or_404(Project, slug=kwargs['slug'])
        else:
            project = get_object_or_404(Project, pk=kwargs['id'])
        id = kwargs['id']
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False).order_by('-id')[:6]
        projects = Project.objects.filter(pk=id)
        pdfFiles = ProjectPDF.objects.filter(projectCategory=id)
        multipleImages = PostImage.objects.filter(post=id)
        for data in multipleImages:
            print(data.image)

        return render(request, self.template_name,
                      {
                          'categories': categories,
                          'charity_categories': charity_categories,
                          'latest_projects': latest_projects,
                          'projects': projects,
                          'pdfFiles': pdfFiles,
                          'multipleImages': multipleImages,
                          'sponsorCategories': sponsorCategories,
                          'totalProjectsInCart': totalProjectsInCart,
                      })

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        numberOfShare = int(request.POST.get('numberOfShare', 0))

        amounts = request.POST.getlist('amount[]', [""])
        # project_category_ids = request.POST.getlist('project_category_id[]')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        project = None

        if 'slug' in kwargs:
            project = get_object_or_404(Project, slug=kwargs['slug'])
        else:
            project = get_object_or_404(Project, pk=kwargs['id'])
            # fetchProject = Project.objects.values('id', 'category__id').filter(pk=kwargs['id'])
            # for data in fetchProject:
            #     print(data)
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        sacrifices = Sacrifice.objects.filter(
            availability__gt=0, project=project).order_by('country').all()
        sacrifices_json_data = Sacrifice.objects.filter(
            availability__gt=0, project=project).values()
        sacrifices_json = json.dumps(
            list(sacrifices_json_data), cls=DjangoJSONEncoder)
        if len(sacrifices_json_data) > 0:
            self.template_name = "web/project_sacrifice_detail_.html"
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'projects': project,
                       'sponsorCategories': sponsorCategories,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'numberOfShare': numberOfShare,
                       'amount': "{0:.3f}".format(float(amounts[0].strip())),
                       # 'project_category_id': int(project_category_ids[0]),
                       'sacrifices_json': sacrifices_json,
                       'sacrifices': sacrifices,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


from django.http import FileResponse, Http404
import os


def openPdf(request, id):
    modelId = id
    objects = ProjectPDF.objects.filter(pk=modelId)
    for data in objects:
        fileName = data.file
        print(fileName)
    filepath = os.path.join('media', str(fileName))
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


class ProjectDoaatDetail(TemplateView):
    template_name = "web/project_detail.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project = get_object_or_404(Project, pk=7)
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'sponsorCategories': sponsorCategories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'project': project,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


def donatedDonation(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_thawab=True).order_by('-id')[:6]
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/donatedonation.html',
                  {
                      'charity_categories': charity_categories,
                      'projects': projects,
                      'cart_projects': cart_projects,
                      'projects_selected': projects_selected,
                      'totalProjectsInCart': totalProjectsInCart,
                  })


class ProjectAishaDetail(TemplateView):
    template_name = "web/project_detail.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project = get_object_or_404(Project, pk=9)
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'sponsorCategories': sponsorCategories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'project': project,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


class ProjectKlaDetail(TemplateView):
    template_name = "web/project_detail.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project = get_object_or_404(Project, pk=8)
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'sponsorCategories': sponsorCategories,
                       'charity_categories': charity_categories,
                       'latest_projects': latest_projects,
                       'project': project,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


def happyStories(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    cart_projects, projects_selected = get_cart(request)
    dataScienceNews = ScienceNews.objects.all().order_by('-id')[:5]
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    return render(request, 'web/happystories.html', {
        'dataScienceNews': dataScienceNews,
        'charity_categories': charity_categories,
        'cart_projects': cart_projects,
    })


class News(TemplateView):
    # template_name = "web/newsPrevious.html"
    template_name = "web/news.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        news = PRNews.objects.all().order_by('-id')[:6]
        if 'category_id' in kwargs:
            news = PRNews.objects.filter(
                category__id=kwargs['category_id']).order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_news = PRNews.objects.all().order_by('-id')[:6]

        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'latest_news': latest_news,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


def joinchat(request):
    if request.method == 'POST':
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        country = request.POST.get('country', '')
        number = request.POST.get('number', '')
        contactChoice = request.POST.get('contactChoice', '')
        joinChat.objects.create(
            country=country,
            whatsappPhone=number,
            contactChoice=contactChoice
        )
        messages.success(request, ('Thanks For Joining Us'))
        return render(request, 'web/joinchat.html', {
            'charity_categories': charity_categories,
        })
    else:
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, 'web/joinchat.html', {
            'charity_categories': charity_categories,
        })


def icalculator(request):
    return render(request, 'web/iqalculator.html')


class NewsDetail(TemplateView):
    template_name = "web/newsdetail.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        obj = get_object_or_404(PRNews, pk=kwargs['id'])
        news = PRNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_news = PRNews.objects.all().order_by('-id')[:6]

        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'latest_news': latest_news,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'obj': obj,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


class ScienceCenter(TemplateView):
    template_name = "web/detailpage.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        news = ScienceNews.objects.all().order_by('-id')[:1]
        obj = get_object_or_404(ScienceNews, pk=kwargs['category_id'])
        # if 'category_id' in kwargs:
        #     news = ScienceNews.objects.filter(
        #         category__id=kwargs['category_id']).order_by('-id')[:1]
        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        science_categories = ScienceCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        latest_news = ScienceNews.objects.all().order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'latest_news': latest_news,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'science_categories': science_categories,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       'obj': obj,
                       })


class Charity(TemplateView):
    template_name = "web/charity.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')
        if 'category_id' in kwargs:
            projects = Project.objects.filter(is_closed=False, is_hidden=False,
                                              category__id=kwargs['category_id'], is_compaign=False).order_by('-id')
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        all_categories = Category.objects.filter(inMenu=True).order_by('-id')
        charity_categories = all_categories.filter(parent=None)
        # topImagess = topImages.objects.all().order_by('-id')[:1]
        latest_projects = Project.objects.filter(
            is_closed=False, is_hidden=False, category__inHomePage=True, is_compaign=False).order_by('-id')[:6]

        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'projects': projects,
                       'sponsorCategories': sponsorCategories,
                       'categories': categories,
                       # 'topImagess': topImagess,
                       'charity_categories': charity_categories,
                       'all_categories': all_categories,
                       'latest_projects': latest_projects,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


def localProjects(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    localProjects = Project.objects.filter(is_closed=False, is_hidden=False, location="Kuwait",
                                           is_sadaqah=False, is_compaign=False).order_by('-id')[:3]
    localProjects2 = Project.objects.filter(is_closed=False, is_hidden=False, location="Kuwait",
                                            is_sadaqah=False, is_compaign=False).order_by('-id')[:4]
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, location="Kuwait", is_sadaqah=True,
                                             is_compaign=False)
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    all_categories = Category.objects.filter(inMenu=True).order_by('-id')
    charity_categories = all_categories.filter(parent=None)
    # topImagess = topImages.objects.all().order_by('-id')[:1]
    cart_projects, projects_selected = get_cart(request)

    # return render(request, 'web/projectsAccordingToCategories.html', {'categoryId': categoryId})
    return render(request, 'web/localProjects.html',
                  {'sliders': sliders,
                   'localProjects': localProjects,
                   'localProjects2': localProjects2,
                   'projectsSadaqah': projectsSadaqah,
                   'sponsorCategories': sponsorCategories,
                   'categories': categories,
                   # 'topImagess': topImagess,
                   'charity_categories': charity_categories,
                   'all_categories': all_categories,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def foreignProjects(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    localProjects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                           is_compaign=False).exclude(
        location="Kuwait").order_by('-id')[:3]
    localProjects2 = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                            is_compaign=False).exclude(
        location="Kuwait").order_by('-id')[:4]
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                             is_compaign=False).exclude(
        location="Kuwait").order_by('-id')[:4]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    all_categories = Category.objects.filter(inMenu=True).order_by('-id')
    charity_categories = all_categories.filter(parent=None)
    # topImagess = topImages.objects.all().order_by('-id')[:1]
    cart_projects, projects_selected = get_cart(request)

    # return render(request, 'web/projectsAccordingToCategories.html', {'categoryId': categoryId})
    return render(request, 'web/foreignProjects.html',
                  {'sliders': sliders,
                   'localProjects': localProjects,
                   'localProjects2': localProjects2,
                   'projectsSadaqah': projectsSadaqah,
                   'sponsorCategories': sponsorCategories,
                   'categories': categories,
                   # 'topImagess': topImagess,
                   'charity_categories': charity_categories,
                   'all_categories': all_categories,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def projectsWithCategories(request, category_id):
    categoryId = category_id
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    allprojects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    all_categories = Category.objects.filter(inMenu=True).order_by('-id')
    charity_categories = all_categories.filter(parent=None)

    categoryOfProjects = Project.objects.values('id', 'category__id')
    # print(categoryOfProjects)
    # for categoryId in all_categories:
    #     print("CATEGORY PARENT:", categoryId.id)
    #     for data in categoryOfProjects:
    #         if data['category__id'] == categoryId.id:
    #             print("PROJECTS OF THAT CATEGORY: ", data['category__id'])
    #             print("PROJECTS OF THAT CATEGORY: ", data['id'])

    # topImagess = topImages.objects.all().order_by('-id')[:1]
    latest_projects = Project.objects.filter(
        is_closed=False, is_hidden=False, category__inHomePage=True, is_compaign=False).order_by('-id')[:6]
    cart_projects, projects_selected = get_cart(request)

    # return render(request, 'web/projectsAccordingToCategories.html', {'categoryId': categoryId})
    return render(request, 'web/projectsAccordingToCategories.html',
                  {'sliders': sliders,
                   'allprojects': allprojects,
                   'sponsorCategories': sponsorCategories,
                   'categories': categories,
                   # 'topImagess': topImagess,
                   'charity_categories': charity_categories,
                   'all_categories': all_categories,
                   'latest_projects': latest_projects,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'categoryOfProjects': categoryOfProjects,
                   'categoryId': categoryId,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def projectsOfParticularCategory(request, category_id):
    categoryId = category_id
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    allprojects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_compaign=False).order_by('-id')
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    all_categories = Category.objects.filter(inMenu=True).order_by('-id')
    categoryName = Category.objects.filter(pk=categoryId)
    for data in categoryName:
        categoryName1 = data.name
    charity_categories = all_categories.filter(parent=None)

    categoryOfProjects = Project.objects.filter(
        category=categoryId, is_hidden=False, is_compaign=False).order_by('-id')
    # print(categoryOfProjects)
    # for categoryId in all_categories:
    #     print("CATEGORY PARENT:", categoryId.id)
    #     for data in categoryOfProjects:
    #         if data['category__id'] == categoryId.id:
    #             print("PROJECTS OF THAT CATEGORY: ", data['category__id'])
    #             print("PROJECTS OF THAT CATEGORY: ", data['id'])

    # topImagess = topImages.objects.all().order_by('-id')[:1]
    latest_projects = Project.objects.filter(
        is_closed=False, is_hidden=False).order_by('-id')[:6]
    cart_projects, projects_selected = get_cart(request)
    employee = Project.objects.all()
    myFilter = ProjectFilter(request.POST, queryset=employee)
    employee = myFilter.qs

    # return render(request, 'web/projectsAccordingToCategories.html', {'categoryId': categoryId})
    return render(request, 'web/allProjectsOfParticularCategory.html',
                  {'sliders': sliders,
                   'allprojects': allprojects,
                   'sponsorCategories': sponsorCategories,
                   'categories': categories,
                   # 'topImagess': topImagess,
                   'charity_categories': charity_categories,
                   'all_categories': all_categories,
                   'latest_projects': latest_projects,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'projects': categoryOfProjects,
                   'categoryId': categoryId,
                   'totalProjectsInCart': totalProjectsInCart,
                   'categoryName1': categoryName1,
                   'getMyCurrency': getMyCurrency,
                   'myFilter': myFilter,
                   'employee': employee,
                   })


class Confirmation(TemplateView):
    template_name = "web/confirmation.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        route = request.POST.get('route', '')
        email = request.POST.get('email', '')
        login_email = request.POST.get('login_email', '')
        login_password = request.POST.get('login_password', '')
        register_email = request.POST.get('register_email', '')
        register_password = request.POST.get('register_password', '')
        register_confirm_password = request.POST.get(
            'register_confirm_password', '')
        register_name = request.POST.get('register_name', '')
        register_phone = request.POST.get('register_phone', '')
        payment_method = request.POST.get('payment_method')
        self.request.session['amounts'] = []
        self.request.session['project_ids'] = []
        self.request.session['project_category_ids'] = []
        now = datetime.now()
        now_plus_60 = now + timedelta(minutes=60.0)
        self.request.session['cart_date'] = now_plus_60.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        project_category_ids = request.POST.getlist('project_category_id[]')
        print(project_category_ids)
        projects = Project.objects.filter(id__in=project_ids)
        project_categories = Category.objects.filter(
            id__in=project_category_ids)

        projects_selected = []
        if 'amounts' not in request.session:
            self.request.session['amounts'] = []
            self.request.session['project_ids'] = []
            self.request.session['project_category_ids'] = []

        session_amounts = self.request.session['amounts']
        session_project_ids = self.request.session['project_ids']
        session_project_category_ids = self.request.session[
            'project_category_ids']

        for i, project_id in enumerate(project_ids):
            amount = amounts[i]
            project_category_id = project_category_ids[i]
            obj = {'id': int(project_id.strip()), 'amount': amount.strip(),
                   'project_category_id': int(project_category_id.strip())}
            projects_selected.append(obj)
            session_amounts.append(obj.get('amount'))
            session_project_ids.append(obj.get('id'))
            session_project_category_ids.append(obj.get('project_category_id'))

        self.request.session['amounts'] = session_amounts
        self.request.session['project_ids'] = session_project_ids
        self.request.session['project_category_ids'] = \
            session_project_category_ids
        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        sliders = Slider.objects.all().order_by('-id')[:5]
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'projects': projects_selected,
                       'projects_detail': projects,
                       'sliders': sliders,
                       'email': email,
                       'login_email': login_email,
                       'login_password': login_password,
                       'register_email': register_email,
                       'register_password': register_password,
                       'register_confirm_password': register_confirm_password,
                       'register_name': register_name,
                       'register_phone': register_phone,
                       'route': route,
                       'project_categories': project_categories,
                       'payment_method': payment_method

                       })


class Checkout(TemplateView):
    template_name = "web/checkout.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        self.request.session['amounts'] = []
        self.request.session['project_ids'] = []
        self.request.session['project_category_ids'] = []
        now = datetime.now()
        now_plus_60 = now + timedelta(minutes=60.0)
        self.request.session['cart_date'] = now_plus_60.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        project_category_ids = request.POST.getlist('project_category_id[]')
        print(project_category_ids)
        projects_selected = []
        if 'amounts' not in request.session:
            self.request.session['amounts'] = []
            self.request.session['project_ids'] = []
            self.request.session['project_category_ids'] = []

        session_amounts = self.request.session['amounts']
        session_project_ids = self.request.session['project_ids']
        session_project_category_ids = self.request.session[
            'project_category_ids']
        for i, project_id in enumerate(project_ids):
            amount = amounts[i]
            project_category_id = project_category_ids[i]
            session_amounts.append(amount)
            session_project_ids.append(project_id)
            session_project_category_ids.append(project_category_id)

        project_ids = session_project_ids
        amounts = session_amounts
        project_category_ids = session_project_category_ids

        for i, project_id in enumerate(project_ids):
            amount = amounts[i]
            project_category_id = project_category_ids[i]
            obj = {'id': int(project_id), 'amount': amount.strip(),
                   'project_category_id': int(project_category_id)}
            projects_selected.append(obj)

        self.request.session['amounts'] = amounts
        self.request.session['project_ids'] = project_ids
        self.request.session['project_category_ids'] = project_category_ids
        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        sliders = Slider.objects.all().order_by('-id')[:5]
        projects = Project.objects.filter(id__in=project_ids)
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'projects': projects_selected,
                       'projects_detail': projects,
                       'sliders': sliders
                       })

    @method_decorator(csrf_protect)
    def get(self, request, *args, **kwargs):
        if 'cart_date' not in request.session:
            self.request.session['amounts'] = []
            self.request.session['project_ids'] = []
            self.request.session['project_category_ids'] = []
            return redirect('/')
        else:
            cart_date = datetime.strptime(
                self.request.session['cart_date'], '%Y-%m-%dT%H:%M:%SZ')
            if datetime.now() > cart_date:
                return redirect('/')

        project_ids = request.session.get('project_ids')
        amounts = request.session.get('amounts')
        project_category_ids = request.session['project_category_ids']

        if 'deleteId' in request.GET:
            deleteId = int(request.GET.get('deleteId', 0))
            if deleteId < len(project_ids):
                project_ids.pop(deleteId)
                amounts.pop(deleteId)
                project_category_ids.pop(deleteId)

        self.request.session['amounts'] = amounts
        self.request.session['project_ids'] = project_ids
        self.request.session['project_category_ids'] = project_category_ids
        projects = Project.objects.filter(pk__in=project_ids)
        project_categories = Project.objects.filter(
            id__in=project_category_ids)
        projects_selected = []
        for i, project_id in enumerate(project_ids):
            amount = amounts[i]
            project_category_id = project_category_ids[i]
            obj = {'id': project_id, 'amount': amount.strip(),
                   'project_category_id': project_category_id}
            projects_selected.append(obj)

        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'projects': projects_selected,
                       'projects_detail': projects,
                       'project_categories': project_categories
                       })


class CheckoutAsGuest(TemplateView):
    template_name = "web/checkout_result.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        email = request.POST.get('email', '')
        payment_method = request.POST.get('payment_method')
        project_category_ids = request.POST.getlist('project_category_id[]')
        phones = helpers.remove_dublicates(request.POST.getlist('phones[]'))
        transaction = Transaction.objects.create(
            status='Pending', payment_method=payment_method)
        for phone in phones:
            SMS.objects.create(transaction=transaction, phone=phone)
        donates = []
        for i, project_id in enumerate(project_ids):
            donate = Donate.objects.create(
                amount=amounts[i], email=email, project_id=int(project_ids[i]),
                transaction=transaction,
                category_id=int(project_category_ids[i]))
            donates.append(donate)

        url, reference, transaction = generate_payment_url(
            request, transaction)
        return redirect(url)
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        request.session['amounts'] = []
        request.session['project_ids'] = []
        projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                          is_compaign=False).order_by('-id')[:3]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'donates': donates,
                       'sponsorCategories': sponsorCategories,
                       })


class CheckoutAsGuestWithTap(TemplateView):
    template_name = "web/checkout_result.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        project_ids = request.POST.getlist('project_id[]')
        amounts = request.POST.getlist('amount[]')
        email = request.POST.get('email', '')
        payment_method = request.POST.get('payment_method')
        project_category_ids = request.POST.getlist('project_category_id[]')
        phones = helpers.remove_dublicates(request.POST.getlist('phones[]'))
        transaction = Transaction.objects.create(
            status='Pending', payment_method=payment_method, is_tap_payment=True)
        for phone in phones:
            SMS.objects.create(transaction=transaction, phone=phone)
        donates = []
        for i, project_id in enumerate(project_ids):
            donate = Donate.objects.create(
                amount=amounts[i], email=email, project_id=int(project_ids[i]),
                transaction=transaction,
                category_id=int(project_category_ids[i]))
            donates.append(donate)

        url, reference, transaction = generate_payment_url_tap(
            request, transaction, payment_method)
        return redirect(url)


class CheckoutWithLogged(TemplateView):
    template_name = "web/credit_card.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        user = request.user
        if user is not None:
            print(request)
            project_ids = request.POST.getlist('project_id[]')
            amounts = request.POST.getlist('amount[]')
            email = request.POST.get('email', '')
            payment_method = request.POST.get('payment_method')
            # payment_method = request.POST.get('payment_method', 'CreditCard')
            project_category_ids = request.POST.getlist(
                'project_category_id[]')
            phones = helpers.remove_dublicates(
                request.POST.getlist('phones[]'))
            names = request.POST.get('fullname', '')
            transaction = Transaction.objects.create(
                status='Pending', payment_method=payment_method)
            for phone in phones:
                SMS.objects.create(transaction=transaction,
                                   phone=phone, name=names)

            donates = []
            for i, project_id in enumerate(project_ids):
                donate = Donate.objects.create(
                    amount=amounts[i], email=email,
                    project_id=int(project_ids[i]),
                    transaction=transaction, user=user,
                    category_id=int(project_category_ids[i]))
                donates.append(donate)

            if payment_method == 'Knet':
                url, reference, transaction = generate_payment_url(
                    request, transaction)
                return redirect(url)

            session_id, amount = generate_credit_card_payment(
                request, transaction)
            categories = PRCategory.objects.all().order_by('-id')
            charity_categories = Category.objects.filter(
                inMenu=True, parent=None).order_by('-id')
            return render(request, self.template_name,
                          {'categories': categories,
                           'charity_categories': charity_categories,
                           'donates': donates,
                           'session_id': session_id,
                           'amount': amount,
                           'transaction_id': transaction.id,
                           'merchant': settings.MASTERCARD_MERCHANT

                           })
        else:
            return redirect('/checkout/')


class CheckoutWithLogin(TemplateView):
    template_name = "web/checkout_result.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        username = request.POST.get('login_email', '')
        password = request.POST.get('login_password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            project_ids = request.POST.getlist('project_id[]')
            amounts = request.POST.getlist('amount[]')
            email = request.POST.get('email', None)
            payment_method = request.POST.get('payment_method')
            project_category_ids = self.request.session['project_category_ids']
            phones = helpers.remove_dublicates(
                request.POST.getlist('phones[]'))
            transaction = Transaction.objects.create(
                status='Pending', payment_method=payment_method)
            for phone in phones:
                SMS.objects.create(transaction=transaction, phone=phone)
            donates = []
            for i, project_id in enumerate(project_ids):
                donate = Donate.objects.create(
                    amount=amounts[i], email=user.email,
                    project_id=int(project_ids[i]),
                    transaction=transaction, user=user,
                    category_id=int(project_category_ids[i]),
                    normal_email=email
                )
                donates.append(donate)

            url, reference, transaction = generate_payment_url(
                request, transaction)
            return redirect(url)
            categories = PRCategory.objects.all().order_by('-id')
            charity_categories = Category.objects.filter(
                inMenu=True, parent=None).order_by('-id')
            request.session['amounts'] = []
            request.session['project_ids'] = []
            return render(request, self.template_name,
                          {'categories': categories,
                           'charity_categories': charity_categories,
                           'donates': donates
                           })
        else:
            return redirect('/checkout/')


def create_user(first_name, last_name, username, email, password, phone):
    user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                    username=username, email=email, password=password)
    profile = Profile.objects.create(user=user, phone=phone)
    if profile is not None:
        return user, profile
    return None


class CheckoutWithRegister(TemplateView):
    template_name = "web/checkout_result.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        username = request.POST.get('register_email', '')
        password = request.POST.get('register_password', '')
        confirm_password = request.POST.get('register_confirm_password', '')
        name = request.POST.get('register_name', '')
        phone = request.POST.get('register_phone', '')
        if password == confirm_password:
            try:
                user_withemail = User.objects.get(email=username)
            except User.DoesNotExist:
                user_withemail = None
            if user_withemail is None:
                user, profile = create_user(username, password, name, phone)

                if profile is not None:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)

                    project_ids = request.POST.getlist('project_id[]')
                    amounts = request.POST.getlist('amount[]')
                    email = request.POST.get('email', '')
                    payment_method = request.POST.get('payment_method')
                    project_category_ids = self.request.session[
                        'project_category_ids']
                    phones = helpers.remove_dublicates(
                        request.POST.getlist('phones[]'))
                    transaction = Transaction.objects.create(
                        status='Pending', payment_method=payment_method)
                    for phone in phones:
                        SMS.objects.create(
                            transaction=transaction, phone=phone)
                    donates = []
                    for i, project_id in enumerate(project_ids):
                        donate = Donate.objects.create(
                            amount=amounts[i], email=user.email,
                            project_id=int(project_ids[i]),
                            transaction=transaction, user=user,
                            category_id=int(project_category_ids[i]))
                        donates.append(donate)

                    url, reference, transaction = generate_payment_url(
                        request, transaction)
                    return redirect(url)
                    categories = PRCategory.objects.all().order_by('-id')
                    charity_categories = Category.objects.filter(
                        inMenu=True, parent=None).order_by('-id')
                    request.session['amounts'] = []
                    request.session['project_ids'] = []
                    return render(request, self.template_name,
                                  {'categories': categories,
                                   'charity_categories': charity_categories,
                                   'donates': donates
                                   })
                else:
                    return redirect('/checkout/')

            else:
                error = "User with email already exists."
                return render(request, self.template_name,
                              {'error': error})
        else:
            return redirect('/checkout/')


def get_cart(request):
    if 'cart_date' not in request.session:
        request.session['amounts'] = []
        request.session['project_ids'] = []
        request.session['project_category_ids'] = []

    else:
        cart_date = datetime.strptime(
            request.session['cart_date'], '%Y-%m-%dT%H:%M:%SZ')
        if datetime.now() > cart_date:
            request.session['amounts'] = []
            request.session['project_ids'] = []
            request.session['project_category_ids'] = []

    project_ids = request.session.get('project_ids')
    amounts = request.session.get('amounts')
    project_category_ids = request.session['project_category_ids']
    if 'deleteId' in request.GET:
        deleteId = int(request.GET.get('deleteId', 0))
        if deleteId < len(project_ids):
            project_ids.pop(deleteId)
            amounts.pop(deleteId)
            project_category_ids.pop(deleteId)

    request.session['amounts'] = amounts
    request.session['project_ids'] = project_ids
    request.session['project_category_ids'] = project_category_ids
    projects = Project.objects.filter(pk__in=project_ids)
    projects_selected = []
    for i, project_id in enumerate(project_ids):
        amount = amounts[i]
        project_category_id = project_category_ids[i]
        obj = {'id': int(project_id), 'amount': amount.strip(),
               'project_category_id': int(project_category_id)}
        projects_selected.append(obj)

    return projects, projects_selected


@csrf_exempt
def RemoveDonate(request):
    project_ids = request.session.get('project_ids')
    amounts = request.session.get('amounts')
    if 'index' in request.POST:
        index = int(request.POST.get('index', 0))
        if index < len(project_ids):
            project_ids.pop(index)
            amounts.pop(index)

    request.session['amounts'] = []
    request.session['project_ids'] = []
    request.session['project_category_ids'] = []


def Login(request):
    authentication_classes = []
    permission_classes = []
    template_name = "web/login.html"

    # @method_decorator(csrf_protect)
    if request.method == 'POST':
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        sliders = Slider.objects.all().order_by('-id')[:5]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        projects = Project.objects.filter(
            is_sadaqah=False, is_compaign=False).order_by('-id')
        projectsSadaqah = Project.objects.filter(
            is_sadaqah=True, is_compaign=False).order_by('-id')
        username = request.POST.get('email', '')
        activationCodeCreateCompaign = request.POST.get('activationCode')
        activationCodeCreateCompaignStr = str(activationCodeCreateCompaign)
        getTheGeneratedCodeFromSession = request.session.get(
            'generatedRandomNumber')
        getTheGeneratedCodeFromSessionStr = str(getTheGeneratedCodeFromSession)
        print("IN SESSION CODE STR:", getTheGeneratedCodeFromSessionStr)
        print("FETCHED FROM POST METHOD CODE STR:",
              activationCodeCreateCompaignStr)
        if activationCodeCreateCompaignStr == getTheGeneratedCodeFromSessionStr:
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                request.session['User_id'] = username
                login(request, user)
                del request.session['generatedRandomNumber']
                # return render(request, 'web/profile.html',
                return render(request, 'web/index2.html',
                              {
                                  'totalProjectsInCart': totalProjectsInCart,
                                  'sliders': sliders,
                                  'categories': categories,
                                  'sponsorCategories': sponsorCategories,
                                  'charity_categories': charity_categories,
                                  'latest_projects': latest_projects,
                                  'news': news,
                                  'science_news': science_news,
                                  'projects': projects,
                                  'projectsSadaqah': projectsSadaqah,
                              })
            else:
                messages = "Username/Password Combination Invalid."
                return render(request, 'web/login.html',
                              {'messages': messages})
        else:
            messages = "Code Doesn't Match."
            return render(request, 'web/login.html',
                          {'messages': messages})

    if request.method == 'GET':
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        projects = Project.objects.filter(
            is_sadaqah=False, is_compaign=False).order_by('-id')
        projectsSadaqah = Project.objects.filter(
            is_sadaqah=True, is_compaign=False).order_by('-id')
        # if 'category_id' in kwargs:
        #     projects = Project.objects.filter(
        #         category__id=kwargs['category_id']).order_by('-id')[:15]
        if request.user.is_authenticated:
            return render(request, 'web/index2.html',
                          {
                              'totalProjectsInCart': totalProjectsInCart,
                              'getMyCurrency': getMyCurrency,
                              'sliders': sliders,
                              'categories': categories,
                              'sponsorCategories': sponsorCategories,
                              'charity_categories': charity_categories,
                              'latest_projects': latest_projects,
                              'news': news,
                              'science_news': science_news,
                              'projects': projects,
                              'projectsSadaqah': projectsSadaqah,
                          })

        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        latest_projects = Project.objects.filter(
            is_compaign=False).order_by('-id')[:6]
        cart_projects, projects_selected = get_cart(request)
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        projects = Project.objects.filter(
            is_sadaqah=False, is_compaign=False).order_by('-id')
        projectsSadaqah = Project.objects.filter(
            is_sadaqah=True, is_compaign=False).order_by('-id')
        return render(request, 'web/login.html',
                      {
                          'totalProjectsInCart': totalProjectsInCart,
                          'getMyCurrency': getMyCurrency,
                          'sliders': sliders,
                          'categories': categories,
                          'sponsorCategories': sponsorCategories,
                          'charity_categories': charity_categories,
                          'latest_projects': latest_projects,
                          'news': news,
                          'science_news': science_news,
                          'projects': projects,
                          'projectsSadaqah': projectsSadaqah,
                      })


class ProfileView(TemplateView):
    template_name = "web/profile.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated is False:
            language = get_language()
            if language == 'ar':
                return redirect('/ar/login/')
            else:
                return redirect('/en/login/')
        else:
            cart = Cart(request)
            totalProjectsInCart = cart.get_total_products()
            # getMyCurrency = getCurrency(request)
            getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
            userId1 = request.user.id
            userId = int(userId1)
            sliders = Slider.objects.all().order_by('-id')[:5]
            categories = PRCategory.objects.all().order_by('-id')
            sponsorCategories = sponsorship.objects.all()
            charity_categories = Category.objects.filter(
                inMenu=True, parent=None).order_by('-id')
            latest_projects = Project.objects.filter(
                is_compaign=False).order_by('-id')[:6]
            cart_projects, projects_selected = get_cart(request)
            news = PRNews.objects.all().order_by('-id')[:6]
            science_news = ScienceNews.objects.all().order_by('-id')[:6]
            projects = Project.objects.filter(
                created_by=userId, is_compaign=False).order_by('-id')
            projectsSadaqah = Project.objects.filter(
                is_sadaqah=True, is_compaign=False).order_by('-id')
            if 'category_id' in kwargs:
                projects = Project.objects.filter(
                    category__id=kwargs['category_id'], is_compaign=False).order_by('-id')[:15]
            return render(request, self.template_name,
                          {'sliders': sliders,
                           'projects': projects,
                           'projectsSadaqah': projectsSadaqah,
                           'categories': categories,
                           'sponsorCategories': sponsorCategories,
                           'charity_categories': charity_categories,
                           'latest_projects': latest_projects,
                           'cart_projects': cart_projects,
                           'projects_selected': projects_selected,
                           'totalProjectsInCart': totalProjectsInCart,
                           'getMyCurrency': getMyCurrency,
                           'news': news,
                           'science_news': science_news,
                           })


class Register(TemplateView):
    template_name = "web/signup.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        # name = request.POST.get('user_name', '')
        phone = request.POST.get('phone', '')
        for user in User.objects.all():
            if user.is_staff == True:
                adminMail = user.email

        if password == confirm_password:
            try:
                user_withemail = User.objects.get(username=username)
            except User.DoesNotExist:
                user_withemail = None
            if user_withemail is None:
                user, profile = create_user(
                    first_name, last_name, username, email, password, phone)
                users = User.objects.filter(username=username)
                for user in users:
                    user.is_active = False
                    # print(user.is_active)
                    user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your MySite Account'
                site_url = 'http://%s/activate/%s/%s' % (
                    current_site.domain, urlsafe_base64_encode(
                        force_bytes(user.pk)),
                    account_activation_token.make_token(user))
                language = get_language()
                if language == 'ar':
                    message = "شكرا لكم للتسجيل في موقعنا لإكمال التسجيل , عليكم تفعيل الحساب من خلال الضغط على الرابط التالي: {}".format(
                        site_url)
                else:
                    message = "Thank you for registration in our website to complete the registration, you have to activate the account by clicking on the activation link: {}".format(
                        site_url)
                emailHostUser = settings.EMAIL_HOST_USER
                send_mail('From Basaier', message, emailHostUser, [username, ])
                print("MAIL SENT FOR ACTIVATIOIN:")
                language = get_language()
                if language == 'ar':
                    messages = 'يرجى تأكيد بريدك الإلكتروني لإكمال التسجيل.'
                else:
                    messages = 'Please Confirm Your Email To Complete Registration.'
                # if profile is not None:
                #     login(request, user)
                #     return redirect('/profile/')
                return render(request, 'web/login.html', {
                    'messages': messages,
                    'totalProjectsInCart': totalProjectsInCart,
                    'getMyCurrency': getMyCurrency,
                })
            else:
                messages = "User with email already exists."
                return render(request, self.template_name,
                              {
                                  'messages': messages,
                                  'totalProjectsInCart': totalProjectsInCart,
                                  'getMyCurrency': getMyCurrency,
                              })

        else:
            language = get_language()
            if language == 'ar':
                return redirect('/ar/register/')
            else:
                return redirect('/en/register/')

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        if request.user.is_authenticated:
            return render(request, 'web/index2.html', {'totalProjectsInCart': totalProjectsInCart, })

        categories = PRCategory.objects.all().order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, self.template_name,
                      {'categories': categories,
                       'charity_categories': charity_categories,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            # user.email_confirmed = True
            user.save()
            login(request, user)
            language = get_language()
            if language == 'ar':
                messages.success(request, ('تم تنشيط حسابك....!'))
                return redirect('/ar')
            else:
                messages.success(
                    request, ('Your Account Have Been Activated....!'))
                return redirect('/en')
        else:
            language = get_language()
            if language == 'ar':
                messages.error(
                    request, ('كان ارتباط التأكيد غير صالح ، ربما لأنه تم استخدامه بالفعل.'))
                return redirect('/')
            else:
                messages.error(request,
                               ('The Confirmation Link Was Invalid, Possibly Because It Has Already Been Used.'))
                return redirect('/')


class ChangePasswordView(TemplateView):
    template_name = "web/changePassword.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if password == confirm_password:
            request.user.set_password(password)
            request.user.save()
            language = get_language()
            if language == 'ar':
                return redirect('/ar/login/')
            else:
                return redirect('/en/login/')
        else:
            error = "Passwords Don't Match"
            return render(request, self.template_name,
                          {'error': error})

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        if not request.user.is_authenticated:
            return render(request, 'web/profile.html', {
                'totalProjectsInCart': totalProjectsInCart,
                'getMyCurrency': getMyCurrency,
            })
        return render(request, self.template_name, {
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })


def aboutUs(request):
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    return render(request, 'web/aboutus.html', {
        'charity_categories': charity_categories,
    })


# class AboutUs(TemplateView):
#     # template_name = "web/about_us.html"
#
#     def get(self, request, *args, **kwargs):
#         cart = Cart(request)
#         totalProjectsInCart = cart.get_total_products()
#         # getMyCurrency = getCurrency(request)
#         getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#         sliders = Slider.objects.all().order_by('-id')[:5]
#         news = PRNews.objects.all().order_by('-id')[:6]
#         science_news = ScienceNews.objects.all().order_by('-id')[:6]
#         boardOfDirectory = boardOfDirectories.objects.all().order_by('-id')[:6]
#         categories = PRCategory.objects.all().order_by('-id')
#         project_dirctories = ProjectsDirectory.objects.all()
#         sponsorCategories = sponsorship.objects.all()
#         charity_categories = Category.objects.filter(
#             inMenu=True, parent=None).order_by('-id')
#
#         cart_projects, projects_selected = get_cart(request)
#         return render(request, self.template_name,
#                       {'sliders': sliders,
#                        'categories': categories,
#                        'charity_categories': charity_categories,
#                        'news': news,
#                        'sponsorCategories': sponsorCategories,
#                        'boardOfDirectory': boardOfDirectory,
#                        'project_dirctories': project_dirctories,
#                        'science_news': science_news,
#                        'cart_projects': cart_projects,
#                        'projects_selected': projects_selected,
#                        'totalProjectsInCart': totalProjectsInCart,
#                        'getMyCurrency': getMyCurrency,
#                        })


class ContactUs(TemplateView):
    template_name = "web/contactus.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        adminMail = settings.EMAIL_HOST_USER
        contact = Contact.objects.create(
            name=name, email=email,
            subject=subject, message=message
        )
        send_mail(subject, message, adminMail, [email, ])
        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, self.template_name,
                      {'sliders': sliders,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })


# class Volunteer(TemplateView):
#     # template_name = "web/volunteerPreviousMaybe.html"
#     template_name = "web/volunteer.html"
#
#     @method_decorator(csrf_protect)
#     def post(self, request, *args, **kwargs):
#         name = request.POST.get('name', '')
#         email = request.POST.get('email', '')
#         currentJob = request.POST.get('currentJob', '')
#         phoneNumber = request.POST.get('phoneNumber', '')
#         highestQualification = request.POST.get('highestQualification', '')
#         address = request.POST.get('address', '')
#         adminMail = settings.EMAIL_HOST_USER
#         if email is not None and name is not None and currentJob is not None and phoneNumber is not None and highestQualification is not None and address is not None:
#             volunteer.objects.create(
#                 name=name,
#                 email=email,
#                 currentJob=currentJob,
#                 phoneNumber=phoneNumber,
#                 highestQualification=highestQualification,
#                 address=address
#             )
#             language = get_language()
#             if language == 'ar':
#                 messages.success(request, ("تم إرسال الرسالة بنجاح.!"))
#             else:
#                 messages.success(request, ("Message Sent Successfully...!"))
#         # contact = Contact.objects.create(
#         #     name=name, email=email,
#         #     subject=subject, message=currentJob
#         # )
#         send_mail(email, address, adminMail, [adminMail, ])
#         return render(request, self.template_name)
#
#     def get(self, request, *args, **kwargs):
#         cart = Cart(request)
#         totalProjectsInCart = cart.get_total_products()
#         # getMyCurrency = getCurrency(request)
#         getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#         sliders = Slider.objects.all().order_by('-id')[:5]
#         news = PRNews.objects.all().order_by('-id')[:6]
#         science_news = ScienceNews.objects.all().order_by('-id')[:6]
#         categories = PRCategory.objects.all().order_by('-id')
#         sponsorCategories = sponsorship.objects.all()
#         charity_categories = Category.objects.filter(
#             inMenu=True, parent=None).order_by('-id')
#         cart_projects, projects_selected = get_cart(request)
#         return render(request, self.template_name,
#                       {'sliders': sliders,
#                        'categories': categories,
#                        'charity_categories': charity_categories,
#                        'news': news,
#                        'sponsorCategories': sponsorCategories,
#                        'science_news': science_news,
#                        'cart_projects': cart_projects,
#                        'projects_selected': projects_selected,
#                        'totalProjectsInCart': totalProjectsInCart,
#                        'getMyCurrency': getMyCurrency,
#                        })

def volunteerNew(request):
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    return render(request, 'web/volunteer.html', {
        'charity_categories': charity_categories,
    })


def volunteerAndSpread(request):
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    if request.method == 'POST':
        name = request.POST.get('name', '')
        civilNumber = request.POST.get('civilNumber', '')
        dateOfBirth = request.POST.get('dateOfBirth', '')
        sex = request.POST.get('sex', '')
        country = request.POST.get('country', '')
        phoneNumber1 = request.POST.get('phoneNumber1', '')
        emergencyPhoneNumber = request.POST.get('emergencyPhoneNumber', '')
        relativeRelation = request.POST.get('relativeRelation', '')
        email = request.POST.get('email', '')
        qualification = request.POST.get('qualification', '')
        specialization = request.POST.get('specialization', '')
        employer = request.POST.get('employer', '')
        currentPosition = request.POST.get('currentPosition', '')
        preferedVolunteeringField = request.POST.get('preferedVolunteeringField', '')
        interset = request.POST.get('interset', '')
        # try:
        obj = volunteer.objects.create(
            name=name,
            civilNumber=civilNumber,
            dateOfBirth=dateOfBirth,
            sex=sex,
            country=country,
            phoneNumber1=phoneNumber1,
            emergencyPhoneNumber=emergencyPhoneNumber,
            relativeRelation=relativeRelation,
            email=email,
            qualification=qualification,
            specialization=specialization,
            employer=employer,
            currentPosition=currentPosition,
            preferedVolunteeringField=preferedVolunteeringField,
            interset=interset,
        )
        messages.success(request, "Data Has Been Sent Successfully...!")
        # except:
        #     messages.success(request, "Please Try Again Later...!")
        #     pass
        return render(request, 'web/volunteerandspread.html', {
            'charity_categories': charity_categories,
        })
    else:
        return render(request, 'web/volunteerandspread.html', {
            'charity_categories': charity_categories,
        })


def joinfieldvolunteer(request):
    if request.method == 'POST':
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, 'web/joinfieldvolunteer.html', {
            'charity_categories': charity_categories,
        })
    else:
        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        return render(request, 'web/joinfieldvolunteer.html', {
            'charity_categories': charity_categories,
        })


def ourPartners(request):
    charity_categories = Category.objects.filter(
        inMenu=True, parent=None).order_by('-id')
    return render(request, 'web/ourpartners.html', {
        'charity_categories': charity_categories,
    })


def Partner(request):
    charity_categories = Category.objects.filter(inMenu=True, parent=None).order_by('-id')
    if request.method == 'POST':
        foreignAffairsNumber = request.POST.get('foreignAffairsNumber', '')
        licenseStartDate = request.POST.get('licenseStartDate', '')
        licenseExpiryDate = request.POST.get('licenseExpiryDate', '')
        entityAr = request.POST.get('entityAr', '')
        entityEn = request.POST.get('entityEn', '')
        entityLocal = request.POST.get('entityLocal', '')
        continent = request.POST.get('continent', '')
        country = request.POST.get('country', '')
        provinceOrState = request.POST.get('provinceOrState', '')
        address = request.POST.get('address', '')
        phoneNumber1 = request.POST.get('phoneNumber1', '')
        phoneNumber2 = request.POST.get('phoneNumber2', '')
        phoneNumber3 = request.POST.get('phoneNumber3', '')
        email = request.POST.get('email', '')
        website = request.POST.get('website', '')
        facebookLink = request.POST.get('facebookLink', '')
        twitterLink = request.POST.get('twitterLink', '')
        instagramLink = request.POST.get('instagramLink', '')
        yearFounded = request.POST.get('yearFounded', '')
        affliatedAuthority = request.POST.get('affliatedAuthority', '')
        branches = request.POST.get('branches', '')
        natureOfEntityWork = request.POST.get('natureOfEntityWork', '')
        employeesInEntity = request.POST.get('employeesInEntity', '')
        projectsImplemented = request.POST.get('projectsImplemented', '')
        prominentGoals = request.POST.get('prominentGoals', '')
        achievements = request.POST.get('achievements', '')
        beneficiarySegments = request.POST.get('beneficiarySegments', '')
        entityManagerName = request.POST.get('entityManagerName', '')
        entityManagerPhoneNumber1 = request.POST.get('entityManagerPhoneNumber1', '')
        entityManagerUsername1 = request.POST.get('entityManagerUsername1', '')
        entityManagerPhoneNumber2 = request.POST.get('entityManagerPhoneNumber2', '')
        entityManagerUsername2 = request.POST.get('entityManagerUsername2', '')
        entityManagerPhoneNumber3 = request.POST.get('entityManagerPhoneNumber3', '')
        entityManagerUsername3 = request.POST.get('entityManagerUsername3', '')
        entityManagerPhoneNumber4 = request.POST.get('entityManagerPhoneNumber4', '')
        donorName = request.POST.get('donorName', '')
        theState1 = request.POST.get('theState1', '')
        donorName2 = request.POST.get('donorName2', '')
        theState2 = request.POST.get('theState2', '')
        donorName3 = request.POST.get('donorName3', '')
        theState3 = request.POST.get('theState3', '')
        donorName4 = request.POST.get('donorName4', '')
        theState4 = request.POST.get('theState4', '')
        nameOfSponsoringParty = request.POST.get('nameOfSponsoringParty', '')
        attachTestimonial = request.FILES["attachTestimonial"]
        try:
            created = partner.objects.create(
                foreignAffairsNumber=foreignAffairsNumber,
                licenseStartDate=licenseStartDate,
                licenseExpiryDate=licenseExpiryDate,
                entityAr=entityAr,
                entityEn=entityEn,
                entityLocal=entityLocal,
                continent=continent,
                country=country,
                provinceOrState=provinceOrState,
                address=address,
                phoneNumber1=phoneNumber1,
                phoneNumber2=phoneNumber2,
                phoneNumber3=phoneNumber3,
                email=email,
                website=website,
                facebookLink=facebookLink,
                twitterLink=twitterLink,
                instagramLink=instagramLink,
                yearFounded=yearFounded,
                affliatedAuthority=affliatedAuthority,
                branches=branches,
                natureOfEntityWork=natureOfEntityWork,
                employeesInEntity=employeesInEntity,
                projectsImplemented=projectsImplemented,
                prominentGoals=prominentGoals,
                achievements=achievements,
                beneficiarySegments=beneficiarySegments,
                entityManagerName=entityManagerName,
                entityManagerPhoneNumber1=entityManagerPhoneNumber1,
                entityManagerUsername1=entityManagerUsername1,
                entityManagerPhoneNumber2=entityManagerPhoneNumber2,
                entityManagerUsername2=entityManagerUsername2,
                entityManagerPhoneNumber3=entityManagerPhoneNumber3,
                entityManagerUsername3=entityManagerUsername3,
                entityManagerPhoneNumber4=entityManagerPhoneNumber4,
                donorName=donorName,
                theState1=theState1,
                donorName2=donorName2,
                theState2=theState2,
                donorName3=donorName3,
                theState3=theState3,
                donorName4=donorName4,
                theState4=theState4,
                nameOfSponsoringParty=nameOfSponsoringParty,
                attachTestimonial=attachTestimonial
            )
            messages.success(request, "BE A PARTNER PROJECT CREATED SUCCESSFULLY...!")
            print("BE A PARTNER PROJECT CREATED SUCCESSFULLY...!")
        except:
            return render(request, 'web/bepartner.html', {'charity_categories': charity_categories, })
        return render(request, 'web/bepartner.html', {'charity_categories': charity_categories, })
    else:
        return render(request, 'web/bepartner.html', {'charity_categories': charity_categories, })


class CreatePeople(View):
    def post(self, request, *args, **kwargs):
        # name = request.POST.get('name', None)
        # phone = request.POST.get('phone', None)
        print(request)
        # person = People.objects.create(name=name, phone=phone)

        # if person:
        #     status = "Success"
        # else:
        status = "Failure"

        data = {'status': status}
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        status = "Failure"

        data = {'status': status}
        return JsonResponse(data)


def arabic_language(request):
    referer = request.META.get('HTTP_REFERER')
    activate('ar')
    return HttpResponseRedirect(referer.replace("/en/", "/ar/"))


def english_language(request):
    referer = request.META.get('HTTP_REFERER')
    activate('en')
    return HttpResponseRedirect(referer.replace("/ar/", "/en/"))


def logout(request):
    django_logout(request)
    return redirect('/')


def get_domain_url(request):
    protocol = 'https' if request.is_secure() else 'http'
    return "://".join([protocol, get_current_site(request).domain])


def get_success_url(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.KNET_SUCCESS_URL])


# def get_success_url(request):
#     site_domain = get_domain_url(request)
#     return "".join([
#         site_domain, "/" + request.LANGUAGE_CODE + "",
#         settings.KNET_SUCCESS_URL])


def get_failure_url(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.KNET_FAILURE_URL])


# def get_failure_url(request):
#     site_domain = get_domain_url(request)
#     return "".join([
#         site_domain, "/" + request.LANGUAGE_CODE + "",
#         settings.KNET_FAILURE_URL])


def get_response_url(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.TAP_RESPONSE_URL])


def get_response_url_of_subscription(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.TAP_RESPONSE_URL])


def get_success_url_tap(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.TAP_SUCCESS_URL])


def get_failure_url_tap(request):
    site_domain = get_domain_url(request)
    return "".join([
        site_domain + settings.TAP_FAILURE_URL])


# def get_response_url(request):
#     site_domain = get_domain_url(request)
#     return "".join([
#         site_domain, "/" + request.LANGUAGE_CODE + "",
#         settings.TAP_RESPONSE_URL])
#
#
# def get_success_url_tap(request):
#     site_domain = get_domain_url(request)
#     return "".join([
#         site_domain, "/" + request.LANGUAGE_CODE + "",
#         settings.TAP_SUCCESS_URL])
#
#
# def get_failure_url_tap(request):
#     site_domain = get_domain_url(request)
#     return "".join([
#         site_domain, "/" + request.LANGUAGE_CODE + "",
#         settings.TAP_FAILURE_URL])


def get_payment_id_and_url(response_content):
    split_list = response_content.split(":")
    payment_id = split_list[0]
    return payment_id, "PaymentID=".join(
        [":".join(split_list[1:]), payment_id])


def generate_payment_url_tap(request, transaction, payment_method):
    try:
        source = "src_kw.knet"
        response_url = get_response_url(request)
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)

        if payment_method != 'Knet':
            source = "src_card"

        # payload = "{\"amount\":"+str(amount)+",\"currency\":\"KWD\",\"reference\":{\"transaction\":\""+str(transaction.id)+"\",\"order\":\"ord_0001\"},\"customer\":{\"first_name\":\"test\",\"middle_name\":\"test\",\"last_name\":\"test\",\"email\":\"test@test.com\",\"phone\":{\"country_code\":\"965\",\"number\":\"50000000\"}},\"source\":{\"id\":\""+source+"\"},\"redirect\":{\"url\":\""+response_url+"\"}}"
        json_payload = {
            "amount": str(amount),
            # "currency": getMyCurrency,
            "currency": "KWD",
            "reference": {
                "transaction": str(transaction.id),
                "order": str(transaction.id),
            },
            "customer": {
                "first_name": donates[0].project.name,
                "middle_name": donates[0].project.name,
                "last_name": donates[0].project.name,
                "email": "test@test.com",
                "phone": {
                    "country_code": "965",
                    "number": "50000000"
                }
            },
            "source": {
                "id": source
            },
            "redirect": {
                "url": response_url
            }}
        headers = {
            'authorization': "Bearer " + settings.TAP_API_KEY,
            'content-type': "application/json"
        }
        payload = json.dumps(json_payload)
        response = requests.request(
            "POST", settings.TAP_PAY_URL, data=payload, headers=headers)
        print(response)
        # if response.status_code != 200:
        #     return None, None, None
        json_data = json.loads(response.text)
        tap_id = json_data["id"]
        payment_url = json_data["transaction"]["url"]
        transaction.tap_id = tap_id
        transaction.save()

        return payment_url, tap_id, transaction
    except Exception as e:
        return None, None, None


def generate_sponsor_payment_url_tap(request, transaction, payment_method, interval, period, fromDate, auto_renew,
                                     timezone, currency, description, customerId):
    try:
        source = "src_kw.knet"
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        response_url = get_response_url_of_subscription(request)
        # post_url = settings.TAP_PAY_SUBSCRIPTION_URL
        amount = 0.0
        generatedToken = request.session.get('generatedTokenId')
        generatedCard = request.session.get('generatedCardId')
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)
            print(amount)

        # if payment_method != 'Knet':
        # source = "src_card"

        json_payload = {
            "term": {
                "interval": str(interval),
                "period": int(period),
                # "from": "2021-02-20T12:42:00",
                "from": fromDate,
                "due": 0,
                "auto_renew": auto_renew,
                # "timezone": str(timezone),
                # "interval": "MONTHLY",
                # "period": 10,
                # "from": "2021-03-20T12:42:00",
                # "due": 0,
                # "auto_renew": True,
                "timezone": "Asia/Kuwait"
            },
            "trial": {
                "days": 2,
                "amount": 0.1
            },
            "charge": {
                "amount": float(amount),
                # "currency": str(currency),
                "description": str(description),
                # "statement_descriptor": "Sample",
                # "amount": 1,
                # "currency": getMyCurrency,
                "currency": "KWD",
                # "description": "Test Description",
                "metadata": {
                    "udf1": "test 1",
                    "udf2": "test 2"
                },
                "reference": {
                    # "transaction": "txn_0001",
                    # "order": "ord_0001"
                    "transaction": str(transaction.id),
                    "order": str(transaction.id)
                },
                "receipt": {
                    "email": True,
                    "sms": False
                },
                "customer": {
                    "id": customerId
                },
                "source": {
                    "id": generatedCard
                },
                "post": {
                    # "url": "http://your_website.com/post_url"
                    "url": response_url
                }
            }
        }
        # payload = "{\"amount\":"+str(amount)+",\"currency\":\"KWD\",\"reference\":{\"transaction\":\""+str(transaction.id)+"\",\"order\":\"ord_0001\"},\"customer\":{\"first_name\":\"test\",\"middle_name\":\"test\",\"last_name\":\"test\",\"email\":\"test@test.com\",\"phone\":{\"country_code\":\"965\",\"number\":\"50000000\"}},\"source\":{\"id\":\""+source+"\"},\"redirect\":{\"url\":\""+response_url+"\"}}"
        headers = {
            # 'authorization': "Bearer sk_test_XKokBfNWv6FIYuTMg5sLPjhJ",
            'authorization': "Bearer " + settings.TAP_API_KEY,
            'content-type': "application/json"
        }
        payload = json.dumps(json_payload)
        response = requests.request(
            "POST", settings.TAP_PAY_SUBSCRIPTION_URL, data=payload, headers=headers)
        print("RESPONSE FROM THE SUBSCRIPTION URL: ", response.status_code)
        # if response.status_code != 200:
        #     return None, None, None
        json_data = json.loads(response.text)
        print(json_data)
        tap_id = json_data["id"]
        payment_url = json_data["transaction"]["url"]
        transaction.tap_id = tap_id
        transaction.save()

        return payment_url, tap_id, transaction
    except Exception as e:
        return None, None, None


def generate_payment_url(request, transaction):
    try:
        response_url = get_success_url(request)
        error_url = get_failure_url(request)
        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)

        response = requests.post(
            url=settings.KNET_PAY_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Charset": "UTF-8",
                "Cache-Control": "no-cache"
            },
            data={
                "id": settings.KNET_ID,
                "password": settings.KNET_PASSWORD,
                "action": 1,
                "amt": amount,
                "currencycode": 414,
                "langid": "ENG",
                "responseURL": response_url,
                "errorURL": error_url,
                "trackId": transaction.pk
            }
        )
        # if response.status_code == 200 and ":" not in response.text:
        #     return None, None, None
        payment_id, payment_url = get_payment_id_and_url(response.text)
        transaction.knet_payment_id = payment_id
        transaction.save()

        return payment_url, payment_id, transaction
    except Exception as e:
        return None, None, None


@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailureTap(View):
    def get(self, request):
        try:
            charity_categories = Category.objects.filter(
                inMenu=True, parent=None).order_by('-id')
            sponsorCategories = sponsorship.objects.all()

            payment_id = request.GET.get("tap_id")
            transaction = Transaction.objects.filter(
                tap_id=payment_id)
            transaction = transaction[0]

            amount = 0.0
            donates = Donate.objects.filter(transaction=transaction)
            for donate in donates:
                amount += float(donate.amount)

            return render(
                request, "web/checkout_result.html",
                {
                    "amount": amount, "reference_id": transaction.reference,
                    "payment_id": transaction.tap_id,
                    "db_id": transaction.id,
                    "merchant_track_id": transaction.id,
                    "success": False,
                    "donates": donates,
                    'charity_categories': charity_categories,
                    'sponsorCategories': sponsorCategories,
                }
            )
        except Exception as e:
            return redirect('/')

    def post(self, request):
        try:
            payment_id = request.POST.get("paymentid")
            update_transaction_details(request)
            return render(
                request, "web/knet_failure.html",
                {
                    "paymentId": payment_id,
                    "failure_url": get_failure_url(request)
                }
            )
        except Exception as e:
            return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailure(View):
    def get(self, request):
        try:
            charity_categories = Category.objects.filter(
                inMenu=True, parent=None).order_by('-id')
            sponsorCategories = sponsorship.objects.all()

            payment_id = request.GET.get("PaymentID")
            transaction = Transaction.objects.filter(
                knet_payment_id=payment_id)
            transaction = transaction[0]

            amount = 0.0
            donates = Donate.objects.filter(transaction=transaction)
            for donate in donates:
                amount += float(donate.amount)

            return render(
                request, "web/checkout_result.html",
                {
                    "amount": amount, "reference_id": transaction.reference,
                    "payment_id": transaction.knet_payment_id,
                    "db_id": transaction.id,
                    "merchant_track_id": transaction.id,
                    "success": False,
                    "donates": donates,
                    'charity_categories': charity_categories,
                    'sponsorCategories': sponsorCategories,
                }
            )
        except Exception as e:
            return redirect('/')

    def post(self, request):
        try:
            payment_id = request.POST.get("paymentid")
            update_transaction_details(request)
            return render(
                request, "web/knet_failure.html",
                {
                    "paymentId": payment_id,
                    "failure_url": get_failure_url(request)
                }
            )
        except Exception as e:
            return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccess(View):
    def get(self, request):
        # try:
        payment_id = request.GET.get("paymentid")
        transaction = Transaction.objects.filter(
            knet_payment_id=payment_id)
        transaction = transaction[0]

        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)

        project = donates[0].project
        update_total_fund_firebase(project)

        request.session['amounts'] = []
        request.session['project_ids'] = []
        cart = Cart(request)
        cart.removeAll()

        fetchProjectName = Donate.objects.filter(
            transaction=transaction).order_by('-id')
        for data in fetchProjectName:
            projectIdFetchedFromDonationTable = data.project.id
            print("projectIdFetchedFromDonationTable",
                  projectIdFetchedFromDonationTable)
        try:
            senderReceiverModel = giftSenderReceiver.objects.filter(
                project=projectIdFetchedFromDonationTable).order_by('-id')[0]
            print("DATA IN MODEL:", senderReceiverModel)
            senderReceiverModel.status = 'Approved'
            senderReceiverModel.save()
        except Exception as e:
            pass

        fetchProjectName = Donate.objects.filter(
            transaction=transaction).order_by('-id')
        for data in fetchProjectName:
            nameProject = data.project.name
            request.session['projectName'] = nameProject

        html_message = loader.render_to_string(
            'web/email.html',
            {
                "amount": amount, "reference_id": transaction.reference,
                "payment_id": transaction.knet_payment_id,
                "db_id": transaction.id,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates
            }
        )
        # try:
        email_subject = 'شكرا لتبرعك مع جمعية بصائر الخيرية'
        to_list = donates[0].email
        adminMail = settings.EMAIL_HOST_USER
        mail = EmailMultiAlternatives(
            email_subject, 'This is message', adminMail, [to_list])
        mail.attach_alternative(html_message, "text/html")
        # except Exception as e:
        #     pass

        # try:
        mail.send()
        print("MAIL SENT AFTER SUCCESS PAYMENT:")
        # except Exception:
        #     pass

        # TO SEND SMS IF THE DONATION WAS AS GIFT:
        if donates[0].recieverPhone is not None:
            fromSender = 'S@basorg'
            fetchProjectName = Donate.objects.filter(
                transaction=transaction).order_by('-id')
            for data in fetchProjectName:
                nameProject = data.project.name
                request.session['projectName'] = nameProject
            projectName = request.session.get('projectName')
            print("IF DONATED AS GIFT:", projectName)
            phoneNumber = donates[0].recieverPhone
            amount = donates[0].amount
            print("IF DONATED AS GIFT PHONE NUMBER:", phoneNumber)
            message = "تم اهداؤكم تبرع في مشروع {} بقيمة {}".format(
                projectName, amount)
            print(message)
            callThat = sendSMS(message, fromSender, phoneNumber)
            # print(callThat)
            if callThat == 200:
                print("Message Delivered")

        # client = boto3.client(
        #     'sns', settings.AWS_SNS_ZONE,
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        # )

        sms = SMS.objects.filter(transaction=transaction)
        for obj in sms:
            try:
                # paymentId = donates[0].transaction_id
                message = 'تم قبول تبرعكم  بقيمة {} رقم العملية {} شكراً لكم'.format(
                    amount, payment_id)

                fromSender = 'S@basorg'
                callThat = sendSMS(message, fromSender, obj.phone)
                if callThat == 200:
                    print("Invoice Message Sent.", callThat)
            except Exception:
                pass

        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        return render(
            request, "web/checkout_result.html",
            {
                "amount": amount, "reference_id": transaction.reference,
                "payment_id": transaction.knet_payment_id,
                "db_id": transaction.pk,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates,
                'charity_categories': charity_categories,
                'sponsorCategories': sponsorCategories,
            }
        )
        # except Exception as e:
        #     return redirect('/')

    def post(self, request):
        try:
            # body_unicode = request.body.decode('utf-8')
            # email(request, body_unicode)
            payment_id = request.POST.get("paymentid", "0")
            result = request.POST.get("result", None)
            update_transaction_details(request)
            if result != "CAPTURED":
                return render(
                    request, "web/knet_failure.html",
                    {
                        "paymentId": payment_id,
                        "failure_url": get_failure_url(request)
                    }
                )

            return render(
                request, "web/knet_success.html",
                {
                    "paymentId": payment_id,
                    "success_url": get_success_url(request)
                }
            )
        except Exception as e:
            return HttpResponse(e)


@method_decorator(csrf_exempt, name='dispatch')
class ResponseTap(View):
    def get(self, request):
        try:
            payment_id = request.GET.get("tap_id")

            url = settings.TAP_PAY_URL + "/" + payment_id
            payload = "{}"
            headers = {'authorization': "Bearer " + settings.TAP_API_KEY}
            response = requests.request(
                "GET", url, data=payload, headers=headers)
            json_data = json.loads(response.text)
            trackid = json_data["reference"]["transaction"]
            result = json_data["status"]
            try:
                obj = Transaction.objects.get(pk=trackid)
                if obj.result is None:
                    obj.tap_id = payment_id
                    obj.result = result
                    donate = Donate.objects.filter(transaction=obj)[0]
                    if result == "CAPTURED":
                        obj.status = "Approved"
                        if donate.sacrifice is not None:
                            sacrifice = Sacrifice.objects.get(
                                pk=donate.sacrifice.pk)
                            sacrifice.availability = sacrifice.availability - donate.qty
                            sacrifice.save()
                    else:
                        obj.status = "Rejected"

                    project = Project.objects.get(id=donate.project.pk)
                    project_remaining = project.remaining()
                    if project_remaining is not None and project_remaining <= 0 and project.is_target_amount() is True:
                        project.is_closed = True
                        project.save()

                    obj.save()

            except Transaction.DoesNotExist:
                return

            if result != "CAPTURED":
                return redirect(get_domain_url(request) + "/tap/failure/?tap_id=" + payment_id)
            else:
                donates = Donate.objects.filter(transaction=obj)
                project = donates[0].project
                update_total_fund_firebase(project)
                return redirect(get_domain_url(request) + "/tap/success/?tap_id=" + payment_id)

        except Exception as e:
            return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessTap(View):
    def get(self, request):
        # try:
        payment_id = request.GET.get("tap_id")

        transaction = Transaction.objects.filter(
            tap_id=payment_id)
        transaction = transaction[0]

        amount = 0.0
        donates = Donate.objects.filter(transaction=transaction)
        for donate in donates:
            amount += float(donate.amount)

        project = donates[0].project
        update_total_fund_firebase(project)

        project_remaining = project.remaining()
        if project_remaining is not None and project_remaining <= 0 and project.is_target_amount() is True:
            project.is_closed = True
            project.save()

        request.session['amounts'] = []
        request.session['project_ids'] = []
        cart = Cart(request)
        cart.removeAll()

        fetchProjectName = Donate.objects.filter(
            transaction=transaction).order_by('-id')
        for data in fetchProjectName:
            projectIdFetchedFromDonationTable = data.project.id
            print("projectIdFetchedFromDonationTable",
                  projectIdFetchedFromDonationTable)
        try:
            senderReceiverModel = giftSenderReceiver.objects.filter(
                project=projectIdFetchedFromDonationTable).order_by('-id')[0]
            print("DATA IN MODEL:", senderReceiverModel)
            senderReceiverModel.status = 'Approved'
            senderReceiverModel.save()
        except Exception as e:
            pass

        html_message = loader.render_to_string(
            'web/email.html',
            {
                "amount": amount, "reference_id": transaction.reference,
                "payment_id": transaction.tap_id,
                "db_id": transaction.id,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates
            }
        )
        # try:
        email_subject = 'شكرا لتبرعك مع جمعية بصائر الخيرية'
        to_list = donates[0].email
        adminMail = settings.EMAIL_HOST_USER
        mail = EmailMultiAlternatives(
            email_subject, 'This is message', adminMail, [to_list])
        mail.attach_alternative(html_message, "text/html")
        # except:
        #     pass

        # try:
        mail.send()
        print("MAIL SENT AFTER SUCCESS PAYMENT:")
        # except Exception:
        #     pass

        # TO SEND SMS IF THE DONATION WAS AS GIFT:
        if donates[0].recieverPhone is not None:
            fromSender = 'S@basorg'
            fetchProjectName = Donate.objects.filter(
                transaction=transaction).order_by('-id')
            for data in fetchProjectName:
                nameProject = data.project.name
                request.session['projectName'] = nameProject
            projectName = request.session.get('projectName')
            print("IF DONATED AS GIFT:", projectName)
            phoneNumber = donates[0].recieverPhone
            amount = donates[0].amount
            print("IF DONATED AS GIFT:", phoneNumber)
            message = "تم اهداؤكم تبرع في مشروع {} بقيمة {}".format(
                projectName, amount)
            print(message)
            callThat = sendSMS(message, fromSender, phoneNumber)
            # print(callThat)
            if callThat == 200:
                print("Message Delivered")

        # client = boto3.client(
        #     'sns', settings.AWS_SNS_ZONE,
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        # )

        sms = SMS.objects.filter(transaction=transaction)
        for obj in sms:
            try:
                # phone = phonenumbers.parse(obj.phone, None)
                # if phonenumbers.is_valid_number(phone):
                # paymentId = donates[0].transaction_id
                message = 'تم قبول تبرعكم  بقيمة {} رقم العملية {} شكراً لكم'.format(
                    amount, payment_id)

                fromSender = 'S@basorg'
                callThat = sendSMS(message, fromSender, obj.phone)
                if callThat == 200:
                    print("Invoice Message Sent.", callThat)
            except Exception:
                pass

        charity_categories = Category.objects.filter(
            inMenu=True, parent=None).order_by('-id')
        sponsorCategories = sponsorship.objects.all()

        return render(
            request, "web/checkout_result.html",
            {
                "amount": amount, "reference_id": transaction.reference,
                "payment_id": transaction.tap_id,
                "db_id": transaction.pk,
                "merchant_track_id": transaction.id,
                "success": True,
                "donates": donates,
                'charity_categories': charity_categories,
                'sponsorCategories': sponsorCategories,
            }
        )
        # except Exception as e:
        #     return redirect('/')

    def post(self, request):
        try:

            json_data = json.loads(request.body)
            payment_id = json_data["id"]
            result = json_data["status"]
            transaction_id = json_data["reference"]["transaction"]
            # update_transaction_details_tap(result, transaction_id, payment_id)
            if result != "CAPTURED":
                return render(
                    request, "web/tap_failure.html",
                    {
                        "paymentId": payment_id,
                        "failure_url": get_failure_url_tap(request)
                    }
                )

            return render(
                request, "web/tap_success.html",
                {
                    "paymentId": payment_id,
                    "success_url": get_success_url_tap(request)
                }
            )
        except Exception as e:
            return HttpResponse(e)


def email(request, body):
    subject = 'post data'
    message = body
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['abdulaziz@q8coders.com', ]
    send_mail(subject, message, email_from, recipient_list)
    return


def update_transaction_details(request):
    paymentid = request.POST.get("paymentid", None)
    result = request.POST.get("result", None)
    auth = request.POST.get("auth", None)
    ref = request.POST.get("ref", None)
    tranid = request.POST.get("tranid", None)
    postdate = request.POST.get("postdate", None)
    trackid = request.POST.get("trackid", None)

    if trackid is None:
        return

    try:
        obj = Transaction.objects.get(pk=trackid)
        if obj.result is None:
            obj.knet_payment_id = paymentid
            obj.result = result
            obj.auth_code = auth
            obj.reference = ref
            obj.trans_id = tranid
            obj.post_date = postdate
            if result == "CAPTURED":
                obj.status = "Approved"
            else:
                obj.status = "Rejected"

            obj.save()

    except Transaction.DoesNotExist:
        return


def update_transaction_details_tap(result, trackid, payment_id):
    if trackid is None:
        return

    try:
        obj = Transaction.objects.get(pk=trackid)
        if obj.result is None:
            obj.tap_id = payment_id
            obj.result = result
            if result == "CAPTURED":
                obj.status = "Approved"
            else:
                obj.status = "Rejected"

            obj.save()

    except Transaction.DoesNotExist:
        return


def update_total_fund_firebase(project):
    pass
    # config = {
    #     "apiKey": "553f4037184cf18490885a33458dc1cdce96b642",
    #     "authDomain": "basaier-8a7fe.firebaseapp.com",
    #     "databaseURL": "https://basaier-8a7fe.firebaseio.com",
    #     "storageBucket": "basaier-8a7fe.appspot.com"
    # }
    #
    # firebase = pyrebase.initialize_app(config)
    #
    # if project.id == 79:
    #     db = firebase.database()
    #     data = {"total_funded": float(project.total_funded())}
    #     db.child("donates").push(data)


# # FOR CAROUSEL IMAGE UPLOAD: MODEL IN web APP:
# def carouselImagesView(request):
#     images = carouselImages.objects.all()
#     return render(request, 'web/index.html', {'images': images})
# # END FOR CAROUSEL IMAGE UPLOAD: MODEL IN web APP:


def zakatPage(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    projects = Project.objects.filter(is_compaign=False).order_by('-id')[:1]
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                      is_compaign=False).order_by('-id')[:3]
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                             is_compaign=False).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    news2 = PRNews.objects.all().order_by('-id')[:4]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    return render(request, 'web/zakatNew.html', {
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
        'projects': projects,
        'sliders': sliders,
        'project_dirctories': project_dirctories,
        'projects': projects,
        'projectsSadaqah': projectsSadaqah,
        'categories': categories,
        'sponsorCategories': sponsorCategories,
        'charity_categories': charity_categories,
    })


def zakatForMoney(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                      is_compaign=False).order_by('-id')[:3]
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                             is_compaign=False).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    news2 = PRNews.objects.all().order_by('-id')[:4]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    return render(request, 'web/zakatForMoney.html', {
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
        'sliders': sliders,
        'project_dirctories': project_dirctories,
        'projects': projects,
        'projectsSadaqah': projectsSadaqah,
        'categories': categories,
        'sponsorCategories': sponsorCategories,
        'charity_categories': charity_categories,
    })


def zakatForGold(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False,
                                      is_compaign=False).order_by('-id')[:3]
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                             is_compaign=False).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    news2 = PRNews.objects.all().order_by('-id')[:4]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    getMyCurrencyStr = str(getMyCurrency)
    getCurrentGoldValue1 = currentGoldValue(request, getMyCurrencyStr)
    getCurrentGoldValue = int(getCurrentGoldValue1)
    print(getCurrentGoldValue)
    return render(request, 'web/zakatForGold.html', {
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
        'getCurrentGoldValue': getCurrentGoldValue,
        'sliders': sliders,
        'project_dirctories': project_dirctories,
        'projects': projects,
        'projectsSadaqah': projectsSadaqah,
        'categories': categories,
        'sponsorCategories': sponsorCategories,
        'charity_categories': charity_categories,
    })


def currentGoldValue(request, getMyCurrencyStr):
    myCurrency = getMyCurrencyStr
    base_currency = myCurrency
    symbol = 'XAU'
    endpoint = 'latest'
    access_key = '1v1l8rqffzyls39y9z3c2tm4fd08u5gmsdh4wfuh9vrq1v3q98poah5yov2x'

    resp = requests.get(
        'https://metals-api.com/api/' + endpoint + '?access_key=' + access_key + '&base=' + base_currency + '&symbols=' + symbol)
    if resp.status_code != 200:
        print("Status Code Not 200, LINE 2519")
    print("GOLD PRICE: LINE 2516: ", resp.text)
    json_data = json.loads(resp.text)
    goldValuePerOunce = json_data['rates']['XAU']
    return goldValuePerOunce


def zakatForCattle(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    return render(request, 'web/zakatForCattle.html', {
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


def zakatForStocks(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    return render(request, 'web/zakatForStocks.html', {
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


# def allProjects(request):
#     cart = Cart(request)
#     totalProjectsInCart = cart.get_total_products()
#     # getMyCurrency = getCurrency(request)
#     getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#     if request.user.is_authenticated:
#         userId1 = request.user.id
#         userId = int(userId1)
#         sliders = Slider.objects.all().order_by('-id')[:5]
#         project_dirctories = ProjectsDirectory.objects.all()
#         news = PRNews.objects.all().order_by('-id')[:6]
#         science_news = ScienceNews.objects.all().order_by('-id')[:6]
#         categories = PRCategory.objects.all().order_by('-id')
#         sponsorCategories = sponsorship.objects.all()
#
#         charity_categories = Category.objects.filter(
#             inMenu=True, inHomePage=True, parent=None
#         ).order_by('-id')
#         cart_projects, projects_selected = get_cart(request)
#
#         current_user = request.user.id
#         # userInDonation = Donate.objects.filter(user=current_user)
#         userIdsFromDonateTable = Donate.objects.all().order_by('-id')
#         # idsOfProject = projectIdsOfUser.values('project_id')
#         # if projectIdsOfUser != '':
#         #     projects = Project.objects.filter(id=projectIdsOfUser, is_hidden=False)
#         # else:
#         #     projects = Project.objects.all()
#         projects = Project.objects.filter(created_by=userId, is_compaign=False).order_by('-id')
#         # I'M CHANGING THE ALL allProjects.html WITH seasonalprojects.html page, for new basaier design.
#         return render(request, 'web/allProjects.html',
#                       {'sliders': sliders,
#                        'projects': projects,
#                        'userIdsFromDonateTable': userIdsFromDonateTable,
#                        'categories': categories,
#                        'charity_categories': charity_categories,
#                        'news': news,
#                        'sponsorCategories': sponsorCategories,
#                        'science_news': science_news,
#                        'cart_projects': cart_projects,
#                        'projects_selected': projects_selected,
#                        'project_dirctories': project_dirctories,
#                        'current_user': current_user,
#                        'totalProjectsInCart': totalProjectsInCart,
#                        'getMyCurrency': getMyCurrency,
#                        })
#     else:
#         language = get_language()
#         if language == 'ar':
#             messages.error(request, 'الرجاء تسجيل الدخول أولا.!')
#             return redirect('/ar/login/')
#         else:
#             messages.error(request, 'Please Login First...!')
#             return redirect('/en/login/')
#     # return render(request, 'web/allProjects.html', {'projects': projects})


def allProjects(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)

    current_user = request.user.id
    userIdsFromDonateTable = Donate.objects.all().order_by('-id')
    projects = Project.objects.filter(
        is_hidden=False, is_thawab=False, projects_dep_email=None).order_by('-id')
    employee = Project.objects.all()
    myFilter = ProjectFilter(request.POST, queryset=employee)
    employee = myFilter.qs
    # I'M CHANGING THE ALL allProjects.html WITH seasonalprojects.html page, for new basaier design.
    return render(request, 'web/seasonalprojects.html',
                  {'sliders': sliders,
                   'projects': projects,
                   'userIdsFromDonateTable': userIdsFromDonateTable,
                   'categories': categories,
                   'charity_categories': charity_categories,
                   'news': news,
                   'sponsorCategories': sponsorCategories,
                   'science_news': science_news,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'project_dirctories': project_dirctories,
                   'current_user': current_user,
                   'totalProjectsInCart': totalProjectsInCart,
                   'myFilter': myFilter,
                   'employee': employee,
                   })


def search_project(request):
    # Search bar on seasonal projects page i.e seasonalprojects.html
    project_data = Project.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    employee = Project.objects.all()
    myFilter = ProjectFilter(request.POST, queryset=employee)
    employee = myFilter.qs
    return render(request, "web/seasonalprojects2.html", {
        # 'searched': searched,
        # 'searched_project': projects,
        'myFilter': myFilter,
        'employee': employee,
        'charity_categories': charity_categories,
    })


# def sponsorshipPage(request, sponsorCategoryId):
#     cart = Cart(request)
#     totalProjectsInCart = cart.get_total_products()
#     getMyCurrency = getCurrency(request)
#     sliders = Slider.objects.all().order_by('-id')[:5]
#     project_dirctories = ProjectsDirectory.objects.all()
#     science_news = ScienceNews.objects.all().order_by('-id')[:6]
#     categories = PRCategory.objects.all().order_by('-id')
#     sponsorCategories = sponsorship.objects.all()
#     sponsorProjects = sponsorshipProjects.objects.filter(category=sponsorCategoryId).order_by('-id')[:6]
#     sponsorshipsPageContent = sponsorshipPageContent.objects.filter(category=sponsorCategoryId)
#     charity_categories = Category.objects.filter(
#         inMenu=True, inHomePage=True, parent=None
#     ).order_by('-id')
#     cart_projects, projects_selected = get_cart(request)
#
#     return render(request, 'web/sponsorshipPage.html', {
#         'sliders': sliders,
#         'project_dirctories': project_dirctories,
#         'science_news': science_news,
#         'categories': categories,
#         'sponsorCategories': sponsorCategories,
#         'charity_categories': charity_categories,
#         'cart_projects': cart_projects,
#         'projects_selected': projects_selected,
#         'sponsorProjects': sponsorProjects,
#         'sponsorCategoryId': sponsorCategoryId,
#         'sponsorshipsPageContent': sponsorshipsPageContent,
#         'totalProjectsInCart': totalProjectsInCart,
#         'getMyCurrency': getMyCurrency,
#     })


def sponsorshipPage(request, sponsorCategoryId):
    if request.method == 'POST':
        cart = Cart(request)
        categoryId = sponsorCategoryId
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                                 is_compaign=False).order_by('-id')
        instanceOfCategory = get_object_or_404(sponsorship, pk=categoryId)
        stringinstanceOfCategory = str(instanceOfCategory)
        print("POST: ", stringinstanceOfCategory)
        sponsorshipsPageContent = sponsorshipPageContent.objects.filter(
            category=categoryId)
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                          is_compaign=False).order_by('-id')[:3]
        if request.POST.get('age') or request.POST.get('gender') or request.POST.get(
                'duration') or request.POST.get('location'):
            if request.POST.get('age') != '':
                age = request.POST.get('age')
            if request.POST.get('duration') != '':
                duration = request.POST.get('duration')
            if request.POST.get('age') != '' and request.POST.get('gender') != '':
                sponsorProjects = sponsorshipProjects.objects.filter(category=instanceOfCategory, age=age,
                                                                     duration=duration).order_by('-id')
            elif request.POST.get('age') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(category=instanceOfCategory,
                                                                     duration=duration).order_by('-id')
            elif request.POST.get('duration') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(category=instanceOfCategory, age=age).order_by(
                    '-id')
        return render(request, 'web/sponsorOrphan.html', {
            'sliders': sliders,
            'projects': projects,
            'projectsSadaqah': projectsSadaqah,
            'project_dirctories': project_dirctories,
            'science_news': science_news,
            'categories': categories,
            'sponsorCategories': sponsorCategories,
            'charity_categories': charity_categories,
            'sponsorProjects': sponsorProjects,
            'sponsorCategoryId': sponsorCategoryId,
            'sponsorshipsPageContent': sponsorshipsPageContent,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
            'stringinstanceOfCategory': stringinstanceOfCategory,
            'categoryId': categoryId,
        })
    else:
        cart = Cart(request)
        categoryId = sponsorCategoryId
        totalProjectsInCart = cart.get_total_products()
        # getMyCurrency = getCurrency(request)
        getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                                 is_compaign=False).order_by('-id')
        instanceOfCategory = get_object_or_404(sponsorship, pk=categoryId)
        stringinstanceOfCategory = str(instanceOfCategory)
        print("GET: ", stringinstanceOfCategory)
        sponsorProjects = sponsorshipProjects.objects.filter(
            category=instanceOfCategory).order_by('-id')[:6]
        sponsorshipsPageContent = sponsorshipPageContent.objects.filter(
            category=categoryId)
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                          is_compaign=False).order_by('-id')[:3]
        cart_projects, projects_selected = get_cart(request)

        return render(request, 'web/sponsorOrphan.html', {
            'sliders': sliders,
            'projects': projects,
            'projectsSadaqah': projectsSadaqah,
            'project_dirctories': project_dirctories,
            'science_news': science_news,
            'categories': categories,
            'sponsorCategories': sponsorCategories,
            'charity_categories': charity_categories,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'sponsorProjects': sponsorProjects,
            'sponsorCategoryId': sponsorCategoryId,
            'sponsorshipsPageContent': sponsorshipsPageContent,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
            'stringinstanceOfCategory': stringinstanceOfCategory,
            'categoryId': categoryId,
        })


# from django.contrib.gis.utils import GeoIP
# from django.template import  RequestContext
# from django.shortcuts import render_to_response
def getSponsorshipProjectIdFromQuickDonateToCreateToken(request):
    if request.user.is_authenticated == True:
        if request.method == 'GET':
            sponsorId = request.GET.get('project_id[]')
            print("Hitted Sponsor Project Id, Line: 3293", sponsorId)
            return allSponsorshipProjects(request, sponsorId)
            # return HttpResponse('')
    else:
        language = get_language()
        if language == 'ar':
            messages.error(request, 'الرجاء تسجيل الدخول أولا.!')
            return redirect('/ar/login/')
        else:
            messages.error(request, 'Please Login First...!')
            return redirect('/en/login/')


def createTokenView(request, sponsorProjectId):
    request.session['sponsorProjectId'] = sponsorProjectId
    if request.user.is_authenticated == True:
        if request.method == 'POST':
            try:
                email = request.user.email
                cardNumber = request.POST.get('cardNumber')
                exp_month = request.POST.get('exp_month')
                exp_year = request.POST.get('exp_year')
                cvc = request.POST.get('cvc')
                name = request.POST.get('name', '')
                country = request.POST.get('country')
                line1 = request.POST.get('line1', '')
                city = request.POST.get('city', '')
                street = request.POST.get('street', '')
                avenue = request.POST.get('avenue', '')
                json_payload = {
                    "card": {
                        "number": cardNumber,
                        "exp_month": exp_month,
                        "exp_year": exp_year,
                        "cvc": cvc,
                        "name": name,
                        "address": {
                            "country": country,
                            "line1": line1,
                            "city": city,
                            "street": street,
                            "avenue": avenue
                        }
                    },
                    "client_ip": ""
                }
                headers = {
                    'authorization': "Bearer" + settings.TAP_API_KEY,
                    # 'authorization': "Bearer sk_test_XKokBfNWv6FIYuTMg5sLPjhJ",
                    'content-type': "application/json"
                }
                payload = json.dumps(json_payload)
                # response = requests.post(settings.TAP_PAY_CREATE_TOKEN_URL, data=json_payload, headers=headers)
                response = requests.request(
                    "POST", settings.TAP_PAY_CREATE_TOKEN_URL, data=payload, headers=headers)
                json_data1 = json.loads(response.text)
                print("TOKEN_ID:", json_data1["id"])
                token_id = json_data1["id"]
                request.session['generatedTokenId'] = token_id
                # FOR SAVING THE CARD, NEED CUSTOMER_ID AND RECENTLY GENERATED TOKEN:
                ifCustomerExits = CustomerIds.objects.filter(email=email)
                for data in ifCustomerExits:
                    customerId = data.customer_id
                    print("CUSTOMER_ID EXISTING ONE:", customerId)
                    request.session['existingCustomerId'] = str(customerId)
                existingCustomerId = request.session.get('existingCustomerId')
                print("EXISTING CUSTOMER ID IN SESSION: ", existingCustomerId)
                if existingCustomerId != None:
                    # conn = http.client.HTTPSConnection("api.tap.company")
                    # payload = "{\"source\":\""+token_id+"\"}"
                    # headers = {
                    #     'authorization': "Bearer sk_test_XKokBfNWv6FIYuTMg5sLPjhJ",
                    #     'content-type': "application/json"
                    # }
                    # conn.request("POST", "/v2/card/%7BexistingCustomerId%7D", payload, headers)
                    # # conn.request("POST", "/v2/card/"+existingCustomerId, payload, headers)
                    # res = conn.getresponse()
                    # # data = res.read()
                    # data = res.read().decode("utf-8")
                    # jsonedData = json.loads(data)
                    # card_id = data['id']
                    # print(card_id)
                    # request.session['generatedCardId'] = card_id
                    # return sponsorParticularPerson(request, sponsorProjectId)

                    # url = "https://api.tap.company/v2/card/"+existingCustomerId
                    # url = "https://api.tap.company/v2/card/%7BexistingCustomerId%7D"
                    # url = "https://api.tap.company/v2/card/{}".format(existingCustomerId)
                    url1 = "https://api.tap.company/v2/card/"
                    url = "{}{}".format(url1, existingCustomerId)
                    payload = "{\"source\":\"" + token_id + "\"}"
                    headers = {
                        # 'authorization': "Bearer sk_test_XKokBfNWv6FIYuTMg5sLPjhJ",
                        'authorization': "Bearer" + settings.TAP_API_KEY,
                        'content-type': "application/json"
                    }
                    response = requests.request(
                        "POST", url, data=payload, headers=headers)
                    print(response)
                    jsonedData = json.loads(response.text)
                    card_id = jsonedData['id']
                    print(card_id)
                    request.session['generatedCardId'] = card_id
                    return sponsorParticularPerson(request, sponsorProjectId)
                else:
                    # CREATE & STORE CUSTOMER:
                    createTheCustomer = create_customer_sponsor_url(request)
                    # email = request.user.email
                    # ifCustomerExits = CustomerIds.objects.filter(email=email)
                    # totalData = ifCustomerExits.count()
                    # for data in ifCustomerExits:
                    #     customerId = data.customer_id
                    #     print("CUSTOMER_ID CREATED ONE, LINE 2648:", customerId)
                    #     request.session['justCreatedCustomerId'] = str(customerId)
                    justCreatedCustomerId = request.session.get(
                        'justCreatedCustomerId')
                    print("justCreatedCustomerId Session LINE: 2651",
                          justCreatedCustomerId)
                    tokenId = request.session.get('generatedTokenId')

                    # conn = http.client.HTTPSConnection("api.tap.company")
                    # payload = "{\"source\":\""+tokenId+"\"}"
                    # headers = {
                    #     'authorization': "Bearer sk_test_XKokBfNWv6FIYuTMg5sLPjhJ",
                    #     'content-type': "application/json"
                    # }
                    # conn.request("POST", "/v2/card/%7BjustCreatedCustomerId%7D", payload, headers)
                    # res = conn.getresponse()
                    # data = res.read().decode("utf-8")
                    # jsonedData2 = json.loads(data)
                    # print("DATA", jsonedData2)
                    # card_id = data['id']
                    # print(card_id)
                    # request.session['generatedCardId'] = card_id
                    # return sponsorParticularPerson(request, sponsorProjectId)

                    # url = "https://api.tap.company/v2/card/"+justCreatedCustomerId
                    # url = "https://api.tap.company/v2/card/%7BjustCreatedCustomerId%7D"
                    # url = "https://api.tap.company/v2/card/{}".format(justCreatedCustomerId)
                    url1 = "https://api.tap.company/v2/card/"
                    url = "{}{}".format(url1, justCreatedCustomerId)
                    payload = "{\"source\":\"" + tokenId + "\"}"
                    headers = {
                        'authorization': "Bearer" + settings.TAP_API_KEY,
                        'content-type': "application/json"
                    }

                    response = requests.request(
                        "POST", url, data=payload, headers=headers)
                    print(response)
                    jsonedData2 = json.loads(response.text)
                    card_id2 = jsonedData2['id']
                    print(card_id2)
                    request.session['generatedCardId'] = card_id2
                    return sponsorParticularPerson(request, sponsorProjectId)
            except Exception as e:
                return redirect('/')
        else:
            cart = Cart(request)
            totalProjectsInCart = cart.get_total_products()
            # getMyCurrency = getCurrency(request)
            getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
            sliders = Slider.objects.all().order_by('-id')[:5]
            project_dirctories = ProjectsDirectory.objects.all()
            science_news = ScienceNews.objects.all().order_by('-id')[:6]
            categories = PRCategory.objects.all().order_by('-id')
            sponsorCategories = sponsorship.objects.all()
            sponsorProjects = sponsorshipProjects.objects.all().order_by(
                '-id')[:6]
            sponsorshipsPageContent = sponsorshipPageContent.objects.all()
            charity_categories = Category.objects.filter(
                inMenu=True, inHomePage=True, parent=None
            ).order_by('-id')
            cart_projects, projects_selected = get_cart(request)
            # ipAddress = get_client_ip(request)
            # print(ipAddress)
            return render(request, 'web/createToken.html', {
                'sliders': sliders,
                'project_dirctories': project_dirctories,
                'science_news': science_news,
                'categories': categories,
                'sponsorCategories': sponsorCategories,
                'charity_categories': charity_categories,
                'cart_projects': cart_projects,
                'projects_selected': projects_selected,
                'sponsorProjects': sponsorProjects,
                'sponsorshipsPageContent': sponsorshipsPageContent,
                'totalProjectsInCart': totalProjectsInCart,
                'sponsorProjectId': sponsorProjectId,
                'getMyCurrency': getMyCurrency,
                # 'ipAddress': ipAddress,
            })
    else:
        language = get_language()
        if language == 'ar':
            messages.error(request, 'الرجاء تسجيل الدخول أولا.!')
            return redirect('/ar/login/')
        else:
            messages.error(request, 'Please Login First...!')
            return redirect('/en/login/')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sponsorParticularPerson(request, particularPersonId):
    cart = Cart(request)
    sliders = Slider.objects.all().order_by('-id')[:5]
    personId = particularPersonId
    # print(personId)
    project_dirctories = ProjectsDirectory.objects.all()
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    sponsorProjects = sponsorshipProjects.objects.all().filter(pk=personId)
    sponsorProjectsCategoryId = sponsorshipProjects.objects.values('id', 'category__id', 'category__category').filter(
        pk=personId)
    for data in sponsorProjectsCategoryId:
        categoryId = data['category__id']
        # categoryIdN = data['category__category']
        print("SPONSOR_PARTICULAR_PERSON: ", categoryId)
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)

    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        if request.method == 'POST':
            personName = request.POST.get('name')
            totalAmount = request.POST.get('totalAmount')
            defaultDuration = request.POST.get('defaultDuration')
            userEmail = request.user.email
            return render(request, 'web/sponsorParticularPerson.html', {
                'sliders': sliders,
                'project_dirctories': project_dirctories,
                'science_news': science_news,
                'categories': categories,
                'sponsorCategories': sponsorCategories,
                'charity_categories': charity_categories,
                'cart_projects': cart_projects,
                'projects_selected': projects_selected,
                'sponsorProjects': sponsorProjects,
                # 'sponsorCategoryId': sponsorCategoryId,
                # 'sponsorshipsPageContent': sponsorshipsPageContent,
                'totalProjectsInCart': totalProjectsInCart,
                'personName': personName,
                'personId': personId,
                'totalAmount': totalAmount,
                'defaultDuration': defaultDuration,
                'categoryId': categoryId,
                'getMyCurrency': getMyCurrency,
            })
    else:
        language = get_language()
        if language == 'ar':
            messages.error(request, 'الرجاء تسجيل الدخول أولا.!')
            return redirect('/ar/login/')
        else:
            messages.error(request, 'Please Login First...!')
            return redirect('/en/login/')


def allSponsorshipProjects(request, sponsorId):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.method == 'POST':
        project_dirctories = ProjectsDirectory.objects.all()
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        sponsorshipsPageContent = sponsorshipPageContent.objects.filter(
            category=sponsorId)
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        sponsorCountries = sponsorshipProjects.objects.values(
            'location').distinct()
        # age gender duration country
        if request.POST.get('age') or request.POST.get('gender') or request.POST.get(
                'duration') or request.POST.get('location'):
            if request.POST.get('age') != '':
                age = request.POST.get('age')
            if request.POST.get('gender') != '':
                gender = request.POST.get('gender')
            if request.POST.get('location') != '':
                location = request.POST.get('location')
            if request.POST.get('duration') != '':
                duration = request.POST.get('duration')

            if request.POST.get('age') != '' and request.POST.get('gender') != '' and request.POST.get(
                    'location') != '' and request.POST.get(
                'duration') != '':
                sponsorProjects = sponsorshipProjects.objects.filter(gender=gender, location=location,
                                                                     duration=duration
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('gender') == '' and request.POST.get(
                    'location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(duration=duration
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('duration') == '' and request.POST.get(
                    'gender') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(location=location).order_by(
                    '-id')
            elif request.POST.get('gender') == '' and request.POST.get('duration') == '' and request.POST.get(
                    'location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(age=age
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('duration') == '' and request.POST.get(
                    'location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(gender=gender
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('duration') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(gender=gender, location=location,
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('gender') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(duration=duration,
                                                                     location=location,
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '' and request.POST.get('location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(duration=duration, gender=gender,
                                                                     ).order_by('-id')
            elif request.POST.get('gender') == '' and request.POST.get('location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(duration=duration,
                                                                     age=age,
                                                                     ).order_by('-id')
            elif request.POST.get('gender') == '' and request.POST.get('duration') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(location=location, age=age,
                                                                     ).order_by('-id')
            elif request.POST.get('location') == '' and request.POST.get('duration') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(gender=gender, age=age,
                                                                     ).order_by('-id')
            elif request.POST.get('age') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(location=location, gender=gender,
                                                                     duration=duration
                                                                     ).order_by('-id')
            elif request.POST.get('gender') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(age=age, location=location,
                                                                     duration=duration
                                                                     ).order_by('-id')
            elif request.POST.get('location') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(age=age, gender=gender,
                                                                     duration=duration
                                                                     ).order_by('-id')
            elif request.POST.get('duration') == '':
                sponsorProjects = sponsorshipProjects.objects.filter(gender=gender, age=age, location=location,
                                                                     ).order_by('-id')

            return render(request, 'web/allSponsorshipProjects.html', {
                'sponsorId': sponsorId,
                'minPrice': request.POST.get('minPrice'),
                'maxPrice': request.POST.get('maxPrice'),
                'country': request.POST.get('country'),
                'project_dirctories': project_dirctories,
                'science_news': science_news,
                'categories': categories,
                'sponsorCategories': sponsorCategories,
                'charity_categories': charity_categories,
                'cart_projects': cart_projects,
                'projects_selected': projects_selected,
                'sponsorProjects': sponsorProjects,
                'sponsorshipsPageContent': sponsorshipsPageContent,
                'sponsorCountries': sponsorCountries,
                'totalProjectsInCart': totalProjectsInCart,
            })
    else:
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        sponsorProjects = sponsorshipProjects.objects.filter(
            category=sponsorId).order_by('-id')[:6]
        sponsorshipsPageContent = sponsorshipPageContent.objects.filter(
            category=sponsorId)
        sponsorCountries = sponsorshipProjects.objects.values(
            'location').distinct()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/allSponsorshipProjects.html', {
            'sponsorId': sponsorId,
            'sliders': sliders,
            'project_dirctories': project_dirctories,
            'science_news': science_news,
            'categories': categories,
            'sponsorCategories': sponsorCategories,
            'charity_categories': charity_categories,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'sponsorProjects': sponsorProjects,
            'sponsorshipsPageContent': sponsorshipsPageContent,
            'sponsorCountries': sponsorCountries,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })


def sponsorshipProjectsFromQuickDonate(request, sponsorId):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    sponsorProjects = sponsorshipProjects.objects.filter(
        id=sponsorId).order_by('-id')
    sponsorshipsPageContent = sponsorshipPageContent.objects.filter(
        category=sponsorId)
    sponsorCountries = sponsorshipProjects.objects.values(
        'location').distinct()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/allSponsorshipProjects.html', {
        'sponsorId': sponsorId,
        'sliders': sliders,
        'project_dirctories': project_dirctories,
        'science_news': science_news,
        'categories': categories,
        'sponsorCategories': sponsorCategories,
        'charity_categories': charity_categories,
        'cart_projects': cart_projects,
        'projects_selected': projects_selected,
        'sponsorProjects': sponsorProjects,
        'sponsorshipsPageContent': sponsorshipsPageContent,
        'sponsorCountries': sponsorCountries,
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


def giftPage(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, category__inHomePage=True, is_compaign=False
    ).order_by('-id')[:1]
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/giftNew.html', {
        'sliders': sliders,
        'projects': projects,
        'categories': categories,
        'charity_categories': charity_categories,
        'news': news,
        'sponsorCategories': sponsorCategories,
        'science_news': science_news,
        'cart_projects': cart_projects,
        'projects_selected': projects_selected,
        'project_dirctories': project_dirctories,
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


def giftProjectPage(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.method != 'POST':
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(
            is_closed=False, is_compaign=False, is_hidden=False, is_share=True
        ).exclude(total_amount=None).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/giftProjectPage.html', {
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })
    else:
        project_dirctories = ProjectsDirectory.objects.all()
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = PRCategory.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)

        if request.POST.get('isShared') or request.POST.get('isZakat') or request.POST.get(
                'projectType') or request.POST.get('isThawab'):
            if request.POST.get('isShared') != '':
                isShared = request.POST.get('isShared')
            if request.POST.get('isZakat') != '':
                is_Zakat = request.POST.get('isZakat')
            if request.POST.get('isThawab') != '':
                isThawab = request.POST.get('isThawab')
            if request.POST.get('projectType') != '':
                projectType = request.POST.get('projectType')

            if request.POST.get('isShared') != '' and request.POST.get('isZakat') != '' and request.POST.get(
                    'isThawab') != '' and request.POST.get(
                'projectType') != '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True,
                    is_share=isShared, isZakat=is_Zakat, is_thawab=isThawab,
                    category=projectType, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('isZakat') == '' and request.POST.get(
                    'isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, category=projectType, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('projectType') == '' and request.POST.get(
                    'isZakat') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, is_thawab=isThawab,
                    is_compaign=False).order_by(
                    'order')
            elif request.POST.get('isZakat') == '' and request.POST.get('projectType') == '' and request.POST.get(
                    'isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, is_share=isShared, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('projectType') == '' and request.POST.get(
                    'isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, isZakat=is_Zakat, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('projectType') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, isZakat=is_Zakat, is_thawab=isThawab,
                    is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('isZakat') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, category=projectType,
                    is_thawab=isThawab, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '' and request.POST.get('isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, category=projectType, isZakat=is_Zakat,
                    is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isZakat') == '' and request.POST.get('isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, category=projectType,
                    is_compaign=False,
                    is_share=isShared,
                ).order_by('-id')
            elif request.POST.get('isZakat') == '' and request.POST.get('projectType') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, is_thawab=isThawab, is_share=isShared,
                    is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isThawab') == '' and request.POST.get('projectType') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True, isZakat=is_Zakat, is_share=isShared,
                    is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isShared') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True,
                    is_thawab=isThawab, isZakat=is_Zakat,
                    category=projectType, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isZakat') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True,
                    is_share=isShared, is_thawab=isThawab,
                    category=projectType, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('isThawab') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True,
                    is_share=isShared, isZakat=is_Zakat,
                    category=projectType, is_compaign=False
                ).order_by('-id')
            elif request.POST.get('projectType') == '':
                projects = Project.objects.filter(
                    is_closed=False, is_hidden=False, category__inHomePage=True,
                    isZakat=is_Zakat, is_share=isShared, is_thawab=isThawab, is_compaign=False
                ).order_by('-id')

            return render(request, 'web/giftProjectPage.html', {
                'minPrice': request.POST.get('minPrice'),
                'maxPrice': request.POST.get('maxPrice'),
                'country': request.POST.get('country'),
                'project_dirctories': project_dirctories,
                'science_news': science_news,
                'categories': categories,
                'sponsorCategories': sponsorCategories,
                'charity_categories': charity_categories,
                'cart_projects': cart_projects,
                'projects_selected': projects_selected,
                'projects': projects,
                'totalProjectsInCart': totalProjectsInCart,
            })


def giftSendGift(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.method != 'POST':
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        # ONLY THE NORMAL PROJECTS WILL BE SHOWN HERE, NOT THE OTHER ONES LIKE is_thawab.
        projects = Project.objects.filter(is_closed=False, is_compaign=False, is_hidden=False,
                                          is_share=True).exclude(total_amount=None).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/giftSendGift.html', {
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })
    else:
        if request.method == 'POST':
            sliders = Slider.objects.all().order_by('-id')[:5]
            project_dirctories = ProjectsDirectory.objects.all()
            news = PRNews.objects.all().order_by('-id')[:6]
            science_news = ScienceNews.objects.all().order_by('-id')[:6]
            categories = Category.objects.all().order_by('-id')
            sponsorCategories = sponsorship.objects.all()
            charity_categories = Category.objects.filter(
                inMenu=True, inHomePage=True, parent=None
            ).order_by('-id')
            cart_projects, projects_selected = get_cart(request)

            if request.POST.get('minPrice') or request.POST.get('maxPrice') or request.POST.get('category'):
                if request.POST.get('minPrice') != '':
                    minPrice = request.POST.get('minPrice')
                if request.POST.get('maxPrice') != '':
                    maxPrice = request.POST.get('maxPrice')
                if request.POST.get('category') != '':
                    categoryId = request.POST.get('category')

                if request.POST.get('minPrice') != '' and request.POST.get('maxPrice') != '' and request.POST.get(
                        'category') != '':
                    projects = Project.objects.filter(total_amount__range=(minPrice, maxPrice),
                                                      category=categoryId, is_thawab=True, is_share=True,
                                                      is_compaign=False)
                elif request.POST.get('minPrice') == '' and request.POST.get('maxPrice') == '':
                    projects = Project.objects.filter(category=categoryId, is_thawab=True, is_share=True,
                                                      is_compaign=False)
                elif request.POST.get('minPrice') == '' and request.POST.get('category') == '':
                    projects = Project.objects.filter(total_amount__lte=maxPrice, is_thawab=True, is_share=True,
                                                      is_compaign=False)
                elif request.POST.get('maxPrice') == '' and request.POST.get('category') == '':
                    projects = Project.objects.filter(total_amount__gte=minPrice, is_thawab=True, is_share=True,
                                                      is_compaign=False)
                elif request.POST.get('minPrice') == '':
                    projects = Project.objects.filter(total_amount__lte=maxPrice, category=categoryId, is_thawab=True,
                                                      is_share=True, is_compaign=False)
                elif request.POST.get('maxPrice') == '':
                    projects = Project.objects.filter(total_amount__gte=minPrice, category=categoryId, is_thawab=True,
                                                      is_share=True, is_compaign=False)
                elif request.POST.get('category') == '':
                    projects = Project.objects.filter(total_amount__range=(minPrice, maxPrice), is_thawab=True,
                                                      is_share=True, is_compaign=False)
                return render(request, 'web/giftSendGift.html', {
                    'sliders': sliders,
                    'projects': projects,
                    'categories': categories,
                    'charity_categories': charity_categories,
                    'news': news,
                    'sponsorCategories': sponsorCategories,
                    'science_news': science_news,
                    'cart_projects': cart_projects,
                    'projects_selected': projects_selected,
                    'project_dirctories': project_dirctories,
                    'totalProjectsInCart': totalProjectsInCart,
                })
            else:
                messages.info(request, 'Please Select A Value!')
                return render(request, 'web/giftSendGift.html', {'totalProjectsInCart': totalProjectsInCart, })


def giftSendSadaqa(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    # ONLY THE NORMAL PROJECTS WILL BE SHOWN HERE, NOT THE OTHER ONES LIKE is_thawab.
    projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True, is_compaign=False).exclude(
        total_amount=None).order_by(
        '-id')[:1]
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = Category.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/giftSendSadaqa.html', {
        'sliders': sliders,
        'projects': projects,
        'categories': categories,
        'charity_categories': charity_categories,
        'news': news,
        'sponsorCategories': sponsorCategories,
        'science_news': science_news,
        'cart_projects': cart_projects,
        'projects_selected': projects_selected,
        'project_dirctories': project_dirctories,
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


def thawab(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_thawab=True, is_compaign=False
    ).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/thawabNew.html',
                  {'sliders': sliders,
                   'projects': projects,
                   'categories': categories,
                   'charity_categories': charity_categories,
                   'news': news,
                   'sponsorCategories': sponsorCategories,
                   'science_news': science_news,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'project_dirctories': project_dirctories,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def thawabContribution(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_compaign=True, active_compaign=True
    ).order_by('-id')[:9]
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/thawabContribution.html',
                  {'sliders': sliders,
                   'projects': projects,
                   'categories': categories,
                   'charity_categories': charity_categories,
                   'news': news,
                   'sponsorCategories': sponsorCategories,
                   'science_news': science_news,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'project_dirctories': project_dirctories,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def thawabProjects(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, is_thawab=True
    ).order_by('-id')[:9]
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/thawabProjects.html',
                  {'sliders': sliders,
                   'projects': projects,
                   'categories': categories,
                   'charity_categories': charity_categories,
                   'news': news,
                   'sponsorCategories': sponsorCategories,
                   'science_news': science_news,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'project_dirctories': project_dirctories,
                   'totalProjectsInCart': totalProjectsInCart,
                   'getMyCurrency': getMyCurrency,
                   })


def thawabCompaigns(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Compaigns.objects.filter(
            is_active=True, is_private=False).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/thawabCompaigns.html',
                      {'sliders': sliders,
                       'projects': projects,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'getMyCurrency': getMyCurrency,
                       })
    else:
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Compaigns.objects.filter(
            is_active=True, is_private=False).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        messages.error(request, "You Must Login First...!")
        return render(request, 'web/login.html', {
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
        })


def privateCompaigns(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        userId = request.user.id
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(
            is_closed=False, is_hidden=True, is_compaign=True, active_compaign=True, created_by=userId
        ).order_by('-id')[:9]
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/privateCompaigns.html',
                      {'sliders': sliders,
                       'projects': projects,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'getMyCurrency': getMyCurrency,
                       })
    else:
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(
            is_closed=False, is_hidden=True, is_compaign=True, active_compaign=True
        ).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        messages.error(request, "You Must Login First...!")
        return render(request, 'web/login.html', {
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
        })


def sharedCompaigns(request, productId):
    cart = Cart(request)
    # projectId = request.GET.get('projectId')
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Project.objects.filter(
        id=productId, is_closed=False, is_compaign=True, active_compaign=True
    ).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = Category.objects.filter(is_compaign=True).order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/sharedCompaigns.html',
                  {'sliders': sliders,
                   'projects': projects,
                   'categories': categories,
                   'charity_categories': charity_categories,
                   'news': news,
                   'sponsorCategories': sponsorCategories,
                   'science_news': science_news,
                   'cart_projects': cart_projects,
                   'projects_selected': projects_selected,
                   'project_dirctories': project_dirctories,
                   'getMyCurrency': getMyCurrency,
                   })


def publicCompaigns(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        userId = request.user.id
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=True, active_compaign=True, created_by=userId
        ).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        return render(request, 'web/publicCompaigns.html',
                      {'sliders': sliders,
                       'projects': projects,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'getMyCurrency': getMyCurrency,
                       })
    else:
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.filter(
            is_closed=False, is_hidden=False, is_compaign=True, active_compaign=True
        ).order_by('-id')
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.filter(is_compaign=True).order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        messages.error(request, "You Must Login First...!")
        return render(request, 'web/login.html', {
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
        })


def createOwnProject(request):
    if request.method == 'POST':
        projectId = request.POST.get('projectId')
        # GENERATE SHAREABLE LINK USER's PARTICULAR PROJECT:
        intProjectId = int(projectId)
        country = request.POST.get('country')
        amountVar = request.POST.get('amount')
        # amountVar = round(float(amount), 3)
        projectName = request.POST.get('projectName')
        relativeRelation = request.POST.get('relativeRelation')
        civilIdPhoto = request.POST.get("civilIdPhoto")
        phoneNumber = request.POST.get('phoneNumber')
        contactMethod = request.POST.getlist('contactMethod')
        contactChoice = str(contactMethod)
        donorName = request.POST.get('donorName')
        donorPhone1 = request.POST.get('donorPhone1')
        donorPhone2 = request.POST.get('donorPhone2')
        address = request.POST.get('address')
        email = request.POST.get('email')
        instance = Project.objects.filter(id=projectId)
        for data in instance:
            detailVar = data.detail
            detailEnVar = data.detailEn
            imageVar = data.image
            print("IMAGE VARIABLE.", imageVar)
        categoryId = instance.values_list('category__id', flat=True)
        for entry in categoryId:
            list_result = entry
        print("CATEGORY NAME:", str(list_result))
        # receive_category = Category.objects.get(id=categoryVar)

        project = Project.objects.create(
            name=projectName,
            nameEn=projectName,
            detail=detailVar,
            detailEn=detailEnVar,
            total_amount=amountVar,
            is_closed=False,
            is_hidden=True,
            image=imageVar,
            # project.category.set(categoryVar),
            location=country,
            projects_dep_email=email,
            # order=orderVar,
            isZakat=False,
            is_share=False,
            is_thawab=False,
            is_compaign=False,
            donater_name=donorName,
            created_by=None,
        )
        # https://stackoverflow.com/questions/47706946/message-title-needs-to-have-a-value-for-field-id-before-this-many-to-many
        project.category.add(list_result)
        justCreatedProjectId = project.pk
        current_site = get_current_site(request)
        site_url = 'http://%s/privateProject/%s/detail' % (
            current_site.domain, justCreatedProjectId)
        print(site_url)
        instance1 = Project.objects.get(id=projectId)
        create = createOwnProjectModel.objects.create(
            project=instance1,
            country=country,
            projectAmount=amountVar,
            projectName=projectName,
            relativeRelation=relativeRelation,
            civilIdPhoto=civilIdPhoto,
            phoneNumber=phoneNumber,
            contactChoice=contactChoice,
            donorName=donorName,
            donorPhoneNumber1=donorPhone1,
            donorPhoneNumber2=donorPhone2,
            address=address,
            email=email,
            generatedLink=site_url
        )

        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        projects = Project.objects.filter(is_hidden=True).order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True).order_by('-id')
        messages.success(request,
                         "Your Request Has Been Sent Successfully, The link will be shared when it will be approved...!")
        return render(request, 'web/createownproject.html', {
            'cart': cart,
            'totalProjectsInCart': totalProjectsInCart,
            'projects': projects,
            'charity_categories': charity_categories,
        })
    else:
        cart = Cart(request)
        totalProjectsInCart = cart.get_total_products()
        projects = Project.objects.filter(
            is_hidden=True, projects_dep_email=None).order_by('-id')
        charity_categories = Category.objects.filter(
            inMenu=True).order_by('-id')
        return render(request, 'web/createownproject.html', {
            'cart': cart,
            'totalProjectsInCart': totalProjectsInCart,
            'projects': projects,
            'charity_categories': charity_categories,
        })


def postAProject(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        projects = Project.objects.all()
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        # projects = Project.objects.all().order_by('-id')[:12]
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        if request.method == 'POST':
            slugVar = request.POST.get('slug')
            nameVar = request.POST.get('name')
            nameEnVar = request.POST.get('nameEn')
            detailVar = request.POST.get('detail')
            detailEnVar = request.POST.get('detailEn')
            totalAmount = request.POST.get('totalAmount')
            totalAmountVar = round(float(totalAmount), 3)
            # print(totalAmountVar)
            isDefinedVar = request.POST.get('isDefined')
            definedAmount = request.POST.get('definedAmount')
            definedAmountVar = round(float(definedAmount), 3)
            # print(definedAmountVar)
            # isClosedVar = request.POST.get('isClosed')
            # imageVar = request.POST.get('largeImage')
            imageVar = request.FILES["largeImage"]
            print("FETCHED FROM POST IMAGE VARIABLE LARGE:", imageVar)
            # imageSmallVar = request.POST.get('smallImage')
            imageSmallVar = request.FILES["smallImage"]
            print("FETCHED FROM POST IMAGE VARIABLE SMALL:", imageSmallVar)
            categoryVar = request.POST.get('category')
            suggestedDonation = request.POST.get('suggestedDonation')
            suggestedDonationVar = round(float(suggestedDonation), 3)
            # print(suggestedDonationVar)
            emailVar = request.POST.get('email')
            # orderVar = request.POST.get('order')
            isZakatVar = request.POST.get('isZakat')
            isShareVar = request.POST.get('isShare')
            isThawabVar = request.POST.get('isThawab')
            # isCompaignVar = request.POST.get('isCompaign')
            shareJump = request.POST.get('shareJump')
            shareJumpVar = round(float(shareJump), 3)
            shareCount = request.POST.get('shareCount')
            shareCountVar = round(float(shareCount), 3)
            deptEmailVar = request.POST.get('deptEmail')
            financeDeptEmailVar = request.POST.get('financeDeptEmail')
            donatorNameVar = request.POST.get('donatorName')
            donatorPhoneVar = request.POST.get('donatorPhone')
            userId = request.user.id
            receive_category = Category.objects.get(id=categoryVar)

            project = Project.objects.create(
                slug=slugVar,
                name=nameVar,
                nameEn=nameEnVar,
                detail=detailVar,
                detailEn=detailEnVar,
                total_amount=totalAmountVar,
                is_defined=isDefinedVar,
                defined_amount=definedAmountVar,
                # is_closed=isClosedVar,
                is_hidden=True,
                image=imageVar,
                image_small=imageSmallVar,
                # project.category.set(categoryVar),
                suggestedDonation=suggestedDonationVar,
                normal_email=emailVar,
                # order=orderVar,
                isZakat=isZakatVar,
                is_share=isShareVar,
                is_thawab=isThawabVar,
                # is_compaign=isCompaignVar,
                share_jump=shareJumpVar,
                share_count=shareCountVar,
                projects_dep_email=deptEmailVar,
                finaince_dep_email=financeDeptEmailVar,
                donater_name=donatorNameVar,
                donater_phone=donatorPhoneVar,
                created_by=userId,
            )
            # WE ARE NOT USING project.save BECAUSE CATEGORY table/model HAS MANY TO MANY RELATION WITH PROJECT MODEL. SO
            # THE CATEGORY MODEL IS TREATING LIKE A PARENT OF PROJECT MODEL, SO WE HAVE TO GET THAT CATEGORY_ID FIRST THEN SAVE
            # THE OTHER PROJECT CREDENTIALS ACCORDING TO THAT GET ID: AND USE .add() METHOD OR MAYBE .set()
            # https://stackoverflow.com/questions/47706946/message-title-needs-to-have-a-value-for-field-id-before-this-many-to-many
            project.category.add(receive_category)
            # project.save()n
            language = get_language()
            if language == 'ar':
                messages.success(request, ("تم إنشاء المشروع بنجاح.!"))
            else:
                messages.success(request, "Project Created Successfully...!")
        return render(request, 'web/postAProject.html',
                      {'sliders': sliders,
                       'projects': projects,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'totalProjectsInCart': totalProjectsInCart,
                       'getMyCurrency': getMyCurrency,
                       })
    else:
        # projects = Project.objects.all()
        sliders = Slider.objects.all().order_by('-id')[:5]
        project_dirctories = ProjectsDirectory.objects.all()
        projects = Project.objects.all().order_by('-id')[:12]
        news = PRNews.objects.all().order_by('-id')[:6]
        science_news = ScienceNews.objects.all().order_by('-id')[:6]
        categories = Category.objects.all().order_by('-id')
        sponsorCategories = sponsorship.objects.all()
        charity_categories = Category.objects.filter(
            inMenu=True, inHomePage=True, parent=None
        ).order_by('-id')
        cart_projects, projects_selected = get_cart(request)
        messages.error(request, ("Please Login First....!"))
        return render(request, 'web/login.html',
                      {'sliders': sliders,
                       'projects': projects,
                       'categories': categories,
                       'charity_categories': charity_categories,
                       'news': news,
                       'sponsorCategories': sponsorCategories,
                       'science_news': science_news,
                       'cart_projects': cart_projects,
                       'projects_selected': projects_selected,
                       'project_dirctories': project_dirctories,
                       'totalProjectsInCart': totalProjectsInCart,
                       })


def thawabCompaignCategoryDetail(request, categoryId):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    categoryId = categoryId
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Compaigns.objects.filter(
        compaignCategory=categoryId, is_active=True).order_by('-id')
    # remainingAmount = Compaigns.checkRemainingProjectLimit(categoryId)
    # for objects in projects:
    # remainingAmount = checkRemainingProjectLimit(categoryId)
    # print("LET'S CHECK THE REMAINING AMOUNT:", remainingAmount)s
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = Category.objects.filter(id=categoryId).order_by('-id')
    # FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
    particularCountry = CompaignCategory.objects.only(
        'country').filter(id=categoryId).distinct()
    # END FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
    categoriesAllData = CompaignCategory.objects.order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    return render(request, 'web/thawabCompaignCategoryDetail.html', {
        'categoryId': categoryId,
        'sliders': sliders,
        'projects': projects,
        'categories': categories,
        'particularCountry': particularCountry,
        'categoriesAllData': categoriesAllData,
        'charity_categories': charity_categories,
        'news': news,
        'sponsorCategories': sponsorCategories,
        'science_news': science_news,
        'cart_projects': cart_projects,
        'projects_selected': projects_selected,
        'project_dirctories': project_dirctories,
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
    })


def generateActivationCode(request):
    randomNumber = random.SystemRandom().randint(100000, 999999)
    print("GENERATED RANDOM NUMBER:", randomNumber)
    fromSender = ''
    phoneNumberOfUser1 = request.POST.get('phoneNumberOfUser')
    # if request.user.is_authenticated:
    #     userId = request.user.id
    #     userInstance = get_object_or_404(User, id=userId)
    #     profile = get_object_or_404(Profile, user=userInstance)
    #     phoneNumberOfUser = profile.phone
    # else:
    #     phoneNumberOfUser = ''
    randomNumberStr = randomNumber
    language = get_language()
    if language == 'ar':
        message = "كود التفعيل الخاص بك  {}".format(randomNumberStr)
    else:
        message = "Your OTP code is {}".format(randomNumberStr)
    callThat = sendSMS(message, fromSender, phoneNumberOfUser1)
    # print(callThat)
    if callThat == 200:
        print("CODE SENT SUCCESFULLY:", randomNumber)
    else:
        print("CODE SENT FAIL:")

    request.session['generatedRandomNumber'] = randomNumber
    return HttpResponse('')


def createCompaignOfParticularCategory(request, categoryId):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projects = Compaigns.objects.filter(
        compaignCategory=categoryId, is_active=True).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = CompaignCategory.objects.filter(id=categoryId).order_by('-id')
    # FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
    particularCountry = CompaignCategory.objects.only(
        'country').filter(id=categoryId).distinct()
    # END FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
    categoriesAllData = CompaignCategory.objects.order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    cart_projects, projects_selected = get_cart(request)
    if request.user.is_authenticated == True:
        if request.method == 'POST':
            if request.user.is_authenticated:
                userId = request.user.id
                userInstance = get_object_or_404(User, id=userId)
                profile = get_object_or_404(Profile, user=userInstance)
                phoneNumberOfUser = profile.phone
            else:
                phoneNumberOfUser = ''
            nameOfDeceasedVar = request.POST.get('nameOfDeceased')
            projectNameVar = request.POST.get('projectName')
            phoneVar = request.POST.get('phone')
            phoneVarStr = str(phoneVar)
            imageVar = request.POST.get('image')
            email = request.POST.get('email')
            descriptionVar = request.POST.get('description')
            total_amount = request.POST.get('total_amount')
            suggestedDonation = request.POST.get('suggestedDonation')
            isPrivate = request.POST.get('isPrivate')
            activationCodeCreateCompaign = request.POST.get(
                'activationCodeCreateCompaign')
            activationCodeCreateCompaignStr = str(activationCodeCreateCompaign)
            suggestedDonationVar = round(float(suggestedDonation), 3)
            getTheGeneratedCodeFromSession = request.session.get(
                'generatedRandomNumber')
            getTheGeneratedCodeFromSessionStr = str(
                getTheGeneratedCodeFromSession)
            print("IN SESSION CODE STR:", getTheGeneratedCodeFromSessionStr)
            print("FETCHED FROM POST METHOD CODE STR:",
                  activationCodeCreateCompaignStr)
            if activationCodeCreateCompaignStr == getTheGeneratedCodeFromSessionStr:
                userId = request.user.id
                compaignCategoryData = CompaignCategory.objects.filter(
                    id=categoryId)
                compaignData = Compaigns.objects.filter(
                    compaignCategory=categoryId, is_active=True)
                countedCompaignData = compaignData.count()
                # print('COUNTED COMPAIGN DATA: ', countedCompaignData)
                # print("LET'S CHECK THE USER ID: ", userId)
                project = Project.objects.create(
                    name=nameOfDeceasedVar,
                    nameEn=nameOfDeceasedVar,
                    detail=descriptionVar,
                    detailEn=descriptionVar,
                    total_amount=total_amount,
                    image=imageVar,
                    # project.category.set(categoryVar),
                    suggestedDonation=suggestedDonationVar,
                    normal_email=email,
                    is_hidden=isPrivate,
                    is_compaign=True,
                    active_compaign=True,
                    donater_phone=phoneVarStr,
                    created_by=userId,
                )
                # compaignModelData.user.set(userId)
                receive_category = Category.objects.get(id=categoryId)
                project.category.add(receive_category)
                language = get_language()
                if language == 'ar':
                    messages.success(request, 'تم إنشاء Compaign بنجاح.!')
                else:
                    messages.success(
                        request, 'Compaign Created Successfully...!')
                request.session['generatedRandomNumber'] = ''
                isSessionDeleted = request.session.get('generatedRandomNumber')
                print("SESSION DELETED....!", isSessionDeleted)
                # return render(request, 'web/createCompaignOfParticularCategory.html', {
                return render(request, 'web/thawabContribution.html', {
                    'categoryId': categoryId,
                    'sliders': sliders,
                    'projects': projects,
                    'categories': categories,
                    'particularCountry': particularCountry,
                    'categoriesAllData': categoriesAllData,
                    'charity_categories': charity_categories,
                    'news': news,
                    'sponsorCategories': sponsorCategories,
                    'science_news': science_news,
                    'cart_projects': cart_projects,
                    'projects_selected': projects_selected,
                    'project_dirctories': project_dirctories,
                    'totalProjectsInCart': totalProjectsInCart,
                    'getMyCurrency': getMyCurrency,
                    'phoneNumberOfUser': phoneNumberOfUser,
                })
            else:
                cart = Cart(request)
                totalProjectsInCart = cart.get_total_products()
                if request.user.is_authenticated:
                    userId = request.user.id
                    userInstance = get_object_or_404(User, id=userId)
                    profile = get_object_or_404(Profile, user=userInstance)
                    phoneNumberOfUser = profile.phone
                else:
                    phoneNumberOfUser = ''
                # getMyCurrency = getCurrency(request)
                getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
                sliders = Slider.objects.all().order_by('-id')[:5]
                project_dirctories = ProjectsDirectory.objects.all()
                projects = Compaigns.objects.filter(
                    compaignCategory=categoryId, is_active=True).order_by('-id')
                news = PRNews.objects.all().order_by('-id')[:6]
                science_news = ScienceNews.objects.all().order_by('-id')[:6]
                categories = CompaignCategory.objects.filter(
                    id=categoryId).order_by('-id')
                # FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
                particularCountry = CompaignCategory.objects.only(
                    'country').filter(id=categoryId).distinct()
                # END FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
                categoriesAllData = CompaignCategory.objects.order_by('-id')
                sponsorCategories = sponsorship.objects.all()
                charity_categories = Category.objects.filter(
                    inMenu=True, inHomePage=True, parent=None
                ).order_by('-id')
                cart_projects, projects_selected = get_cart(request)
                language = get_language()
                if language == 'ar':
                    messages.warning(
                        request, 'لم يتطابق الرمز ، حاول مرة أخرى.!')
                else:
                    messages.warning(
                        request, 'The Code Did Not Match, Try Again...!')

                cart = Cart(request)
                totalProjectsInCart = cart.get_total_products()
                return render(request, 'web/createCompaignOfParticularCategory.html', {
                    'categoryId': categoryId,
                    'sliders': sliders,
                    'projects': projects,
                    'categories': categories,
                    'particularCountry': particularCountry,
                    'categoriesAllData': categoriesAllData,
                    'charity_categories': charity_categories,
                    'news': news,
                    'sponsorCategories': sponsorCategories,
                    'science_news': science_news,
                    'cart_projects': cart_projects,
                    'projects_selected': projects_selected,
                    'project_dirctories': project_dirctories,
                    'totalProjectsInCart': totalProjectsInCart,
                    'getMyCurrency': getMyCurrency,
                    'phoneNumberOfUser': phoneNumberOfUser,
                })
        else:
            cart = Cart(request)
            totalProjectsInCart = cart.get_total_products()
            # getMyCurrency = getCurrency(request)
            getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
            categoryId = categoryId
            sliders = Slider.objects.all().order_by('-id')[:5]
            project_dirctories = ProjectsDirectory.objects.all()
            projects = Compaigns.objects.filter(
                compaignCategory=categoryId, is_active=True).order_by('-id')
            news = PRNews.objects.all().order_by('-id')[:6]
            science_news = ScienceNews.objects.all().order_by('-id')[:6]
            categories = CompaignCategory.objects.filter(
                id=categoryId).order_by('-id')
            # FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
            particularCountry = CompaignCategory.objects.only(
                'country').filter(id=categoryId).distinct()
            # END FOR FETCHING COUNTRY FROM ABOVE CATEGORY ID:
            categoriesAllData = CompaignCategory.objects.order_by('-id')
            sponsorCategories = sponsorship.objects.all()
            charity_categories = Category.objects.filter(
                inMenu=True, inHomePage=True, parent=None
            ).order_by('-id')
            cart_projects, projects_selected = get_cart(request)
            if request.user.is_authenticated:
                userId = request.user.id
                userInstance = get_object_or_404(User, id=userId)
                profile = get_object_or_404(Profile, user=userInstance)
                phoneNumberOfUser = profile.phone
            else:
                phoneNumberOfUser = ''
            return render(request, 'web/createCompaignOfParticularCategory.html', {
                'categoryId': categoryId,
                'sliders': sliders,
                'projects': projects,
                'categories': categories,
                'particularCountry': particularCountry,
                'categoriesAllData': categoriesAllData,
                'charity_categories': charity_categories,
                'news': news,
                'sponsorCategories': sponsorCategories,
                'science_news': science_news,
                'cart_projects': cart_projects,
                'projects_selected': projects_selected,
                'project_dirctories': project_dirctories,
                'totalProjectsInCart': totalProjectsInCart,
                'getMyCurrency': getMyCurrency,
                'phoneNumberOfUser': phoneNumberOfUser,
            })
    else:
        messages.error(request, 'Please Login First...!')
        return render(request, 'web/login.html', {
            'categoryId': categoryId,
            'sliders': sliders,
            'projects': projects,
            'categories': categories,
            'particularCountry': particularCountry,
            'categoriesAllData': categoriesAllData,
            'charity_categories': charity_categories,
            'news': news,
            'sponsorCategories': sponsorCategories,
            'science_news': science_news,
            'cart_projects': cart_projects,
            'projects_selected': projects_selected,
            'project_dirctories': project_dirctories,
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })


def giftRecieverAndSender(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    if request.user.is_authenticated == True:
        if request.method == 'POST':
            recieverNameVar = request.POST.get('recieverName')
            recieverPhoneVar = request.POST.get('recieverPhone')
            yourMessageToHimVar = request.POST.get('yourMessageToHim')
            fromSender = "+96590900055"
            callThat = sendSMS(yourMessageToHimVar,
                               fromSender, recieverPhoneVar)
            # print(callThat)
            if callThat == 200:
                messages.success(
                    request, 'Your Message Delivered Successfully...!')
                return render(request, 'web/giftRecieverAndSender.html')
            else:
                messages.error(
                    request, 'Your Message Could Not Be Delivered...!')
                return render(request, 'web/giftRecieverAndSender.html')
        else:
            userName = request.user.get_full_name()
            # print(userName)
            # userPhone = request.user.profile.phone
            # print(userPhone)
            return render(request, 'web/giftRecieverAndSender.html', {
                'userName': userName,
                # 'userPhone': userPhone,
                'totalProjectsInCart': totalProjectsInCart,
                'getMyCurrency': getMyCurrency,
            })

    else:
        messages.error(request, "Please Login First...!")
        return render(request, 'web/login.html', {
            'totalProjectsInCart': totalProjectsInCart,
            'getMyCurrency': getMyCurrency,
        })


from web.cart import Cart


# @require_POST
def cart_add_for_gift(request):
    cart = Cart(request)
    if request.method == 'POST':
        id = request.POST.get('project_id')
        selectedAmount = request.POST.get('amount')
        senderNameDonatedDonationPage = request.POST.get(
            'senderNameDonatedDonationPage')
        receiverNameDonatedDonationPage = request.POST.get(
            'receiverNameDonatedDonationPage')
        phoneNumberDonatedDonationPage = request.POST.get(
            'phoneNumberDonatedDonationPage')
        emailDonatedDonationPage = request.POST.get('emailDonatedDonationPage')
        instance = Project.objects.get(id=id)
        insert = giftSenderReceiver.objects.create(
            project=instance,
            amount=selectedAmount,
            sender=senderNameDonatedDonationPage,
            receiver=receiverNameDonatedDonationPage,
            phoneNumber=phoneNumberDonatedDonationPage,
            email=emailDonatedDonationPage
        )
        # projectId = Project.objects.get(id=id)
        # insert.project.add(projectId)

        product = get_object_or_404(Project, id=id)
        totalProjectsInCart = cart.get_total_products()
        # projects = Project.objects.filter(id=id)
        if cart != '':
            cart.add(product=product, selectAmount=selectedAmount,
                     quantity=1, override_quantity=False)
            # messages.success(request, 'Cart Has Been Added Successfully...!')
            # return render(request, 'web/add_to_cart.html', {
            #     'totalProjectsInCart': totalProjectsInCart,
            # })
            # return JsonResponse({'status': 'OK'})
            print("Countered Add Cart...!")
            return HttpResponse('')
    else:
        # messages.error(request, 'Your Cart Could Not Be Added...!')
        # return JsonResponse({'status': 'Fail'})
        return HttpResponse('')


def cart_add(request):
    cart = Cart(request)
    if request.method == 'POST':
        id = request.POST.get('project_id')
        selectedAmount = request.POST.get('amount')
        product = get_object_or_404(Project, id=id)
        totalProjectsInCart = cart.get_total_products()
        # form = CartAddProductForm(request.POST)
        # if form.is_valid():
        #     cd = form.cleaned_data
        if cart != '':
            cart.add(product=product, selectAmount=selectedAmount,
                     quantity=1, override_quantity=False)
            # messages.success(request, 'Cart Has Been Added Successfully...!')
            # return render(request, 'web/add_to_cart.html', {
            #     'totalProjectsInCart': totalProjectsInCart,
            # })
            # return JsonResponse({'status': 'OK'})
            print("Countered Add Cart...!")
            return HttpResponse('')
    else:
        # messages.error(request, 'Your Cart Could Not Be Added...!')
        # return JsonResponse({'status': 'Fail'})
        return HttpResponse('')


@require_POST
def cart_remove(request, id):
    cart = Cart(request)
    product = get_object_or_404(Project, id=id)
    cart.remove(product)
    totalProjectsInCart = cart.get_total_products()
    # return render(request, 'web/add_to_cart.html', {
    #     'totalProjectsInCart': totalProjectsInCart,
    # })
    language = get_language()
    if language == 'ar':
        messages.success(request, 'تمت إزالة عربة التسوق بنجاح.!')
        return redirect('/ar/cart_detail')
    else:
        messages.success(request, 'Cart Has Been Removed Successfully...!')
        return redirect('/en/cart_detail')


@require_POST
def cart_update(request, id):
    cart = Cart(request)
    selectedAmount = request.POST.get('amount[]')
    print(selectedAmount)
    product = get_object_or_404(Project, id=id)
    totalProjectsInCart = cart.get_total_products()
    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    if cart != '':
        cart.update(product=product, selectAmount=selectedAmount,
                    quantity=1, override_quantity=False)
        # return render(request, 'web/add_to_cart.html', {
        #     'totalProjectsInCart': totalProjectsInCart,
        # })
        language = get_language()
        if language == 'ar':
            messages.success(request, 'تم تحديث عربة التسوق بنجاح ...!')
            return redirect('/ar/cart_detail')
        else:
            messages.success(request, 'Cart Has Been Updated Successfully...!')
            return redirect('/en/cart_detail')
    else:
        language = get_language()
        if language == 'ar':
            messages.error(request, 'تم تحديث عربة التسوق بنجاح.!')
            return redirect('/ar/cart_detail')
        else:
            messages.error(request, 'Your Cart Could Not Be Updated...!')
            return redirect('/en/cart_detail')


def removeAll(request):
    cart = Cart(request)
    cart.removeAll()
    totalProjectsInCart = cart.get_total_products()
    # return render(request, 'web/add_to_cart.html', {
    #     'totalProjectsInCart': totalProjectsInCart,
    # })
    language = get_language()
    if language == 'ar':
        messages.success(request, 'تمت إزالة عربات التسوق بنجاح.!')
        return redirect('/ar/checkoutDetail')
    else:
        messages.success(request, 'Carts Have Been Removed Successfully...!')
        return redirect('/en/checkoutDetail')


def cart_detail(request):
    cart = Cart(request)
    projects = Project.objects.filter(
        is_closed=False, is_hidden=False, category__inHomePage=True, is_sadaqah=False, is_compaign=False).order_by(
        '-id')
    totalProjectsInCart = cart.get_total_products()
    print(totalProjectsInCart)
    # getMyCurrency = getCurrency(request)
    getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
    sliders = Slider.objects.all().order_by('-id')[:5]
    project_dirctories = ProjectsDirectory.objects.all()
    projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
                                             is_compaign=False).order_by('-id')
    news = PRNews.objects.all().order_by('-id')[:6]
    news2 = PRNews.objects.all().order_by('-id')[:4]
    science_news = ScienceNews.objects.all().order_by('-id')[:6]
    categories = PRCategory.objects.all().order_by('-id')
    sponsorCategories = sponsorship.objects.all()
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    # cust = get_object_or_404(Customer, id=id)
    # for item in cart:
    #     item['update_quantity_form'] = CartAddProductForm(initial={
    #         'quantity': item['quantity'],
    #         'override': True})
    return render(request, 'web/add_to_cart.html', {
        'cart': cart,
        'projects': projects,
        'totalProjectsInCart': totalProjectsInCart,
        'getMyCurrency': getMyCurrency,
        'sliders': sliders,
        'project_dirctories': project_dirctories,
        'projectsSadaqah': projectsSadaqah,
        'news': news,
        'news2': news2,
        'science_news': science_news,
        'categories': categories,
        'sponsorCategories': sponsorCategories,
        'charity_categories': charity_categories,
    })


# def checkoutDetail(request):
#     cart = Cart(request)
#     totalProjectsInCart = cart.get_total_products()
#     # getMyCurrency = getCurrency(request)
#     getMyCurrency = request.session.get('fetchedCurrencyFromAjax')
#     sliders = Slider.objects.all().order_by('-id')[:5]
#     project_dirctories = ProjectsDirectory.objects.all()
#     projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False, is_compaign=False).order_by(
#         '-id')[:3]
#     projectsSadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True,
#                                              is_compaign=False).order_by('-id')
#     news = PRNews.objects.all().order_by('-id')[:6]
#     news2 = PRNews.objects.all().order_by('-id')[:4]
#     science_news = ScienceNews.objects.all().order_by('-id')[:6]
#     categories = PRCategory.objects.all().order_by('-id')
#     sponsorCategories = sponsorship.objects.all()
#     charity_categories = Category.objects.filter(
#         inMenu=True, inHomePage=True, parent=None
#     ).order_by('-id')
#     if request.user.is_authenticated:
#         userId = request.user.id
#         userInstance = get_object_or_404(User, id=userId)
#         profile = get_object_or_404(Profile, user=userInstance)
#         phoneNumberOfUser = profile.phone
#     else:
#         phoneNumberOfUser = ''
#     # print("PHONE NUMBER OF THE USER:", phoneNumberOfUser)
#     # cust = get_object_or_404(Customer, id=id)
#     # for item in cart:
#     #     item['update_quantity_form'] = CartAddProductForm(initial={
#     #         'quantity': item['quantity'],
#     #         'override': True})
#     return render(request, 'web/cartCheckoutDetailPage.html', {
#         'cart': cart,
#         'projects': projects,
#         'totalProjectsInCart': totalProjectsInCart,
#         'getMyCurrency': getMyCurrency,
#         'sliders': sliders,
#         'project_dirctories': project_dirctories,
#         'news': news,
#         'news2': news2,
#         'science_news': science_news,
#         'categories': categories,
#         'sponsorCategories': sponsorCategories,
#         'charity_categories': charity_categories,
#         'phoneNumberOfUser': phoneNumberOfUser,
#     })


def checkoutDetail(request):
    cart = Cart(request)
    totalProjectsInCart = cart.get_total_products()
    # projects = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=False, is_compaign=False).order_by(
    #     '-id')
    charity_categories = Category.objects.filter(
        inMenu=True, inHomePage=True, parent=None
    ).order_by('-id')
    # if request.user.is_authenticated:
    #     userId = request.user.id
    #     userInstance = get_object_or_404(User, id=userId)
    #     profile = get_object_or_404(Profile, user=userInstance)
    #     phoneNumberOfUser = profile.phone
    # else:
    #     phoneNumberOfUser = ''
    # print("PHONE NUMBER OF THE USER:", phoneNumberOfUser)
    # cust = get_object_or_404(Customer, id=id)
    # for item in cart:
    #     item['update_quantity_form'] = CartAddProductForm(initial={
    #         'quantity': item['quantity'],
    #         'override': True})
    return render(request, 'web/donationbasket.html', {
        'cart': cart,
        # 'projects': projects,
        'totalProjectsInCart': totalProjectsInCart,
        'charity_categories': charity_categories,
        # 'phoneNumberOfUser': phoneNumberOfUser,
    })


def getValuesAccordingToSelectedCategory(request):
    if request.method == 'GET':
        id = request.GET.get('categoryId')
        print("FetchedId", id)
        instanceCategory = get_object_or_404(Category, pk=id)
        projectsData = Project.objects.filter(
            category=instanceCategory, is_compaign=False)
        results = []
        try:
            for r in projectsData:
                results.append(r.id)
                results.append(r.name)
                # data = json.dumps(results)
            # CONVERT IN ARRAY OF DICTIONARIES:
            converted = [{'id': v, 'name': s}
                         for v, s in zip(results[::2], results[1::2])]
            # print("CONVERTED:", converted)
            data = json.dumps(converted)
            mimetype = 'application/json'
            return HttpResponse(data, mimetype)
        except:
            return HttpResponse('Sorry Error Occured...!')


def getValuesAccordingToSelectedCategoryInCreateOwnProject(request):
    if request.method == 'GET':
        id = request.GET.get('categoryId')
        print("FetchedId", id)
        projectsData = Project.objects.get(
            id=id, is_compaign=False)
        values = {'amountVar': projectsData.total_amount, 'countryVar': projectsData.location}
        print(values)
        return JsonResponse(values)


def getSponsoshipValuesAccordingToSelectedCategory(request):
    if request.method == 'GET':
        id = request.GET.get('categoryId1')
        print("FetchedSponssorCategoryId", id)
        instanceCategory = get_object_or_404(sponsorship, pk=id)
        projectsData = sponsorshipProjects.objects.filter(
            category=instanceCategory)
        results = []
        try:
            for r in projectsData:
                results.append(r.id)
                results.append(r.name)
                # data = json.dumps(results)
            # CONVERT IN ARRAY OF DICTIONARIES:
            converted = [{'id': v, 'name': s}
                         for v, s in zip(results[::2], results[1::2])]
            # print("CONVERTED:", converted)
            data = json.dumps(converted)
            mimetype = 'application/json'
            return HttpResponse(data, mimetype)
        except:
            return HttpResponse('Sorry Error Occured...!')
