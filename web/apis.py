# FROM EXISTING VIEWS.PY, THE IMPORTS:
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
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView  # Import TemplateView
from django.views.generic import View
from rest_framework.utils import json

from news.models import Profile
from news.models import Slider, PRNews, PRCategory, \
    ScienceCategory, ScienceNews
from people.models import Contact
from projects.models import Project, Category, \
    Transaction, Donate, ProjectsDirectory, SMS, Sacrifice, sponsorship, sponsorshipProjects, sponsorshipPageContent, \
    CompaignCategory, Compaigns, Profile
from web.models import boardOfDirectories, influencerImages

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_text
# FROM EXISTING VIEWS.PY, THE IMPORTS:


# FROM REST FRAMEWORK IMPORTS:
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

# from .models import SuperUser
from django.contrib.auth.models import User
from django.contrib import messages
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from drf_multiple_model.views import ObjectMultipleModelAPIView

from .serializers import RegisterSerializer, LoginSerializer, ProjectSerializer, slidersSerializer, \
    project_dirctoriesSerializer, newsSerializer, science_newsSerializer, categoriesSerializer, \
    sponsorCategoriesSerializer, charity_categoriesSerializer, sponsorshipProjectsSerializer, \
    profileSerializer


# FROM REST FRAMEWORK IMPORTS:

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    print(request.data)
    serializer = RegisterSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        serializer.save()
        # THIS IS HOW WE GET THE SERIALIZED DATA: (HERE GETTING EMAIL:)
        # print(serializer.validated_data['email'])
        serializedEmail = serializer.validated_data['email']
        # token = Token.objects.get(user=account).key
        # data['token'] = token
        for user in User.objects.all():
            if user.is_staff == True:
                adminMail = user.email
        users = User.objects.filter(email=serializedEmail)
        for user in users:
            user.is_active = False
            user.save()
        current_site = get_current_site(request)
        subject = 'Activate Your MySite Account'
        site_url = 'http://%s/apiActivate/%s/%s' % (
            current_site.domain, urlsafe_base64_encode(force_bytes(user.pk)),
            account_activation_token.make_token(user))
        message = site_url
        send_mail(subject, message, adminMail, [serializedEmail, ])
        # messages.success(request, 'Please Confirm Your Email To Complete Registration.')
        data['response'] = f"Please Confirm Your Email To Complete Registration....!"
    else:
        data = serializer.errors
    return Response(data)


class ActivateAccount2(View):
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
            messages.success(request, 'Your Account Have Been Activated....!')
            print('Your Account Have Been Activated....!')
            return redirect('/api/profile2/')
        else:
            messages.error(request, 'The Confirmation Link Was Invalid, Possibly Because It Has Already Been Used.')
            return redirect('/api/index2/')


@permission_classes([AllowAny])
class CustomAuthToken(ObtainAuthToken):
    serializer_class1 = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class1(data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        # token, created = Token.objects.get_or_create(user=user)
        return Response({
            # 'token': token.key,
            'user_id': user.pk,
            'email': user.email,
        })


class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            token = request.POST.get('token')
            user = User.objects.get(auth_token=token)
            print(user)
            # SuperUser.objects.filter(id=userid).update(auth_token='')
            user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = Response({"detail": _("Successfully logged out.")},
                            status=status.HTTP_200_OK)
        return response


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['GET'])
@permission_classes([AllowAny])
def homePage(request):
    projects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                      is_sadaqah=False).order_by('-id')
    projects_serializer = ProjectSerializer(projects, many=True)
    sadaqah = Project.objects.filter(is_closed=False, is_hidden=False, is_sadaqah=True)[:1]
    sadaqahSerializer = ProjectSerializer(sadaqah, many=True)
    initiativesThawab = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                               is_thawab=True).order_by('-id')
    project_categories = Category.objects.filter(inMenu=True, inHomePage=True, parent=None).order_by('-id')
    project_categories_serializer = charity_categoriesSerializer(project_categories, many=True)
    initiativesThawabSerializer = ProjectSerializer(initiativesThawab, many=True)
    news = PRNews.objects.all().order_by('-id')
    news_serializer = newsSerializer(news, many=True)
    science_news = ScienceNews.objects.all().order_by('-id')[:2]
    science_news_serializer = science_newsSerializer(science_news, many=True)
    # news_categories = PRCategory.objects.all().order_by('-id')
    # news_categories_serializer = categoriesSerializer(news_categories, many=True)
    sponsorshipProjectsMix = sponsorshipProjects.objects.all().order_by('-id')
    sponsorshipProjectsMixSerializer = sponsorshipProjectsSerializer(sponsorshipProjectsMix, many=True)
    sponsorship_categories = sponsorship.objects.all().order_by('-id')
    sponsorship_categories_serializer = sponsorCategoriesSerializer(sponsorship_categories, many=True)
    return Response({
        'projects': projects_serializer.data,
        'projectCategories': project_categories_serializer.data,
        'news': news_serializer.data,
        'initiativesThawab': initiativesThawabSerializer.data,
        'scienceNews': science_news_serializer.data,
        # 'newsCategories': news_categories_serializer.data,
        'sponsorshipMix': sponsorshipProjectsMixSerializer.data,
        'sponsorshipCategories': sponsorship_categories_serializer.data,
        'sadaqah': sadaqahSerializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def externalInitiative(request):
    thawabProjects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                            is_sadaqah=False, is_thawab=True).exclude(location="Kuwait").order_by('-id')
    thawabProjectsSerializer = ProjectSerializer(thawabProjects, many=True)
    giftProjects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                          is_sadaqah=False).exclude(location="Kuwait").order_by('-id')
    giftProjectsSerializer = ProjectSerializer(giftProjects, many=True)
    return Response({
        'externalThawabProjects': thawabProjectsSerializer.data,
        'externalGiftProjects': giftProjectsSerializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def externalProjects(request):
    projects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                      is_sadaqah=False).exclude(location="Kuwait").order_by('-id')
    projectsSerializer = ProjectSerializer(projects, many=True)
    project_categories = Category.objects.filter(inMenu=True, inHomePage=True, parent=None).order_by('-id')
    project_categories_serializer = charity_categoriesSerializer(project_categories, many=True)
    return Response({
        'externalProjects': projectsSerializer.data,
        'projectCategories': project_categories_serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def payZakat(request):
    projects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
                                      isZakat=True).order_by('order')
    projects_serializer = ProjectSerializer(projects, many=True)
    return Response(projects_serializer.data)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def dailySadaqa(request):
#     projects = Project.objects.filter(is_closed=False, is_hidden=False, category__inHomePage=True,
#                                       is_thawab=True).order_by('order')
#     projects_serializer = ProjectSerializer(projects, many=True)
#     return Response(projects_serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
# HERE WE WILL SHOW THE SPONSORSHIP PROJECTS: WHOSE CATEGORY IS `FAMILY`:
def sponsorAFamily(request):
    sponsorshipCategories = get_object_or_404(sponsorship, category='Family')
    print(sponsorshipCategories.id)
    sponsorshipProjectsObject = sponsorshipProjects.objects.filter(category__id=sponsorshipCategories.id).order_by(
        '-id')
    projects_serializer = sponsorshipProjectsSerializer(sponsorshipProjectsObject, many=True)
    return Response({
        'sponsorFamily': projects_serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
# HERE WE WILL SHOW THE SPONSORSHIP PROJECTS: WHOSE CATEGORY IS `ORPHAN`:
def sponsorAnOrphan(request):
    sponsorshipCategories = get_object_or_404(sponsorship, category='Orphan')
    print(sponsorshipCategories.id)
    sponsorshipProjectsObject = sponsorshipProjects.objects.filter(category__id=sponsorshipCategories.id).order_by(
        '-id')
    projects_serializer = sponsorshipProjectsSerializer(sponsorshipProjectsObject, many=True)
    return Response({
        'sponsorOrphan': projects_serializer.data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
# HERE WE WILL SHOW THE SPONSORSHIP PROJECTS: WHOSE CATEGORY IS `ORPHAN`:
def sponsorshipsAccordingToCategory(request, categoryId):
    sponsorshipCategories = get_object_or_404(sponsorship, pk=categoryId)
    print(sponsorshipCategories.id)
    sponsorshipProjectsObject = sponsorshipProjects.objects.filter(category__id=sponsorshipCategories.id).order_by(
        '-id')
    projects_serializer = sponsorshipProjectsSerializer(sponsorshipProjectsObject, many=True)
    sponsorship_categories = sponsorship.objects.all()
    sponsorship_categories_serializer = sponsorCategoriesSerializer(sponsorship_categories, many=True)
    return Response({
        'sponsorshipsAccordingToCategory': projects_serializer.data,
        'sponsorhsipCategories': sponsorship_categories_serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
# HERE WE WILL SHOW THE SPONSORSHIP PROJECTS: WHOSE CATEGORY IS `ORPHAN`:
def sponsorships(request):
    sponsorshipProjectsObject = sponsorshipProjects.objects.all().order_by('-id')
    projects_serializer = sponsorshipProjectsSerializer(sponsorshipProjectsObject, many=True)
    sponsorship_categories = sponsorship.objects.all()
    sponsorship_categories_serializer = sponsorCategoriesSerializer(sponsorship_categories, many=True)
    return Response({
        'sponsorshipProjects': projects_serializer.data,
        'sponsorhsipCategories': sponsorship_categories_serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
# HERE WE WILL SHOW THE SPONSORSHIP PROJECTS: WHOSE CATEGORY IS `ORPHAN`:
def profile2(request):
    if request.user.is_authenticated == True:
        userId = request.user.pk
    profileObject = Profile.objects.filter(pk=userId).order_by('-id')
    profileSerializerData = profileSerializer(profileObject, many=True)
    return Response(profileSerializerData.data)
