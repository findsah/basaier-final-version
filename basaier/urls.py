"""basaier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from filebrowser.sites import site
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from web import views
from web import apis
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import url, include
from people.rest import CreatePeople
from web.views import zakatPage

admin.site.site_header = 'Basaier Admin Panel'
admin.site.site_title = 'Basaier Admin Panel'

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [path('i18n/', include('django.conf.urls.i18n')),
               path('createPeople/', CreatePeople.as_view(),
               name='createPeople'), ]


urlpatterns += i18n_patterns(
    path('admin/filebrowser/', site.urls),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('', views.Index.as_view(), name='index'),
    path('project/<int:id>/detail',
         views.ProjectDetail.as_view(), name='project-detail'),
    path('openPdf/<int:id>',
         views.openPdf, name='openPdf'),
    path('donatedDonation', views.donatedDonation, name="donatedDonation"),
    path('localProjects', views.localProjects, name='localProjects'),
    path('foreignProjects', views.foreignProjects, name='foreignProjects'),
    path('news/<int:id>/detail',
         views.NewsDetail.as_view(), name='news-detail'),
    path('news/<int:category_id>', views.News.as_view(), name='news-category'),
    path('news', views.News.as_view(), name='news'),
    path('happyStories', views.happyStories, name='happyStories'),
    path('joinchat', views.joinchat, name='joinchat'),
    path('icalculator', views.icalculator, name='icalculator'),
    path('createOwnProject', views.createOwnProject, name='createOwnProject'),
    path('science-center/', views.ScienceCenter.as_view(),
         name='science-center'),
    path('science-center/<int:category_id>',
         views.ScienceCenter.as_view(), name='science-center-category'),
    path('charity/', views.Charity.as_view(), name='charity'),
    path('projectWithCategory/<int:category_id>', views.projectsWithCategories,
         name='charity-category'),
    path('projectsOfParticularCategory/<int:category_id>', views.projectsOfParticularCategory,
         name='projectsOfParticularCategory'),
    path('checkout/', views.Checkout.as_view(), name='checkout'),
    path('checkout/confirmation/guest/', views.OnlinePayment.as_view(),
         name='checkout-as-guest'),
    path('checkout/confirmation/guest/tap/', views.OnlinePaymentTap.as_view(),
         name='checkout-as-guest-tap'),
    path('checkout/confirmation/sponsor/tap/', views.OnlineSubscriptionTap.as_view(),
         name='OnlineSubscriptionTap'),
    path('checkout/confirmation/login/', views.CheckoutWithLogin.as_view(),
         name='checkout-login'),
    path('checkout/confirmation/register/', views.CheckoutWithRegister.as_view(),
         name='checkout-register'),
    path('checkout/confirmation/logged/', views.CheckoutWithLogged.as_view(),
         name='checkout-logged'),
    path('remove/donate/', views.RemoveDonate, name='remove-donate'),
    path('login/', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('language/arabic/', views.arabic_language, name='to-arabic'),
    path('language/english', views.english_language, name='to-english'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.logout, name='logout'),
    path('knet/success/', views.PaymentSuccess.as_view(), name='knet-success'),
    path('tap/success/', views.PaymentSuccessTap.as_view(), name='tap-success'),
    path('tap/response/', views.ResponseTap.as_view(), name='tap-response'),
    path('credit-card/success/', views.PaymentSuccessOfCreditCard.as_view(), name='creditcard-success'),
    path('knet/failure/', views.PaymentFailure.as_view(), name='knet-failure'),
    path('tap/failure/', views.PaymentFailureTap.as_view(), name='tap-failure'),
    path('changePassword/', views.ChangePasswordView.as_view(),
         name='changePassword'),
    path('aboutUs', views.aboutUs, name='aboutUs'),
    path('contact-us', views.ContactUs.as_view(), name='contactUs'),
    path('volunteer/', views.volunteerNew, name='volunteer'),
    path('partner', views.Partner, name='partner'),
    path('ourPartners', views.ourPartners, name='ourPartners'),
    path('checkout/confirmation/', views.Confirmation.as_view(), name='confirmation'),
    path('doaat', views.ProjectDoaatDetail.as_view(), name='doaat'),
    path('kla', views.ProjectKlaDetail.as_view(), name='kla'),
    path('aisha', views.ProjectAishaDetail.as_view(), name='aisha'),
    path('<slug:slug>/', views.ProjectDetail.as_view(), name='project_detail_slug'),
    path('zakat', views.zakatPage, name="zakat"),
    path('zakatForMoney', views.zakatForMoney, name="zakatForMoney"),
    path('zakatForGold', views.zakatForGold, name="zakatForGold"),
    path('zakatForCattle', views.zakatForCattle, name="zakatForCattle"),
    path('zakatForStocks', views.zakatForStocks, name="zakatForStocks"),
    path('allProjects', views.allProjects, name="allProjects"),
    path('projectsAccordingToCategories', views.projectsWithCategories, name="projectsAccordingToCategories"),
    path('sponsorshipPage/<int:sponsorCategoryId>', views.sponsorshipPage, name='sponsorshipPage'),
    # path('createToken/<int:sponsorProjectId>', views.createTokenView, name='createTokenView'),
    path('createToken/<int:sponsorProjectId>', views.createTokenView, name='createTokenView'),
    path('getSponsorshipProjectIdFromQuickDonateToCreateToken', views.getSponsorshipProjectIdFromQuickDonateToCreateToken, name='getSponsorshipProjectIdFromQuickDonateToCreateToken'),
    path('allSponsorshipProjects/<int:sponsorId>', views.allSponsorshipProjects, name='allSponsorshipProjects'),
    path('sponsorshipProjectsFromQuickDonate/<int:sponsorId>', views.sponsorshipProjectsFromQuickDonate, name='sponsorshipProjectsFromQuickDonate'),
    path('sponsorParticularPerson/<int:particularPersonId>', views.sponsorParticularPerson, name='sponsorParticularPerson'),
    path('gift', views.giftPage, name="gift"),
    path('giftProjectPage', views.giftProjectPage, name="giftProjectPage"),
    path('giftSendGift', views.giftSendGift, name="giftSendGift"),
    path('giftRecieverAndSender', views.giftRecieverAndSender, name='giftRecieverAndSender'),
    path('giftSendSadaqa', views.giftSendSadaqa, name="giftSendSadaqa"),
    path('activate/<uidb64>/<token>/', views.ActivateAccount.as_view(), name='activate'),
    path('thawab', views.thawab, name='thawab'),
    path('thawabContribution', views.thawabContribution, name='thawabContribution'),
    path('thawabProjects', views.thawabProjects, name='thawabProjects'),
    path('thawabCompaigns', views.thawabCompaigns, name='thawabCompaigns'),
    path('publicCompaigns', views.publicCompaigns, name='publicCompaigns'),
    path('privateCompaigns', views.privateCompaigns, name='privateCompaigns'),
    path('privateCompaigns/<int:productId>', views.sharedCompaigns, name='sharedCompaigns'),
    path('publicCompaigns/<int:productId>', views.sharedCompaigns, name='sharedCompaigns'),
    path('postAProject', views.postAProject, name='postAProject'),
    path('thawabCompaignCategoryDetail/<int:categoryId>', views.thawabCompaignCategoryDetail, name='thawabCompaignCategoryDetail'),
    path('createCompaignOfParticularCategory/<int:categoryId>', views.createCompaignOfParticularCategory, name='createCompaignOfParticularCategory'),
    path('cart_add', views.cart_add, name='cart_add'),
    path('cart_remove/<int:id>', views.cart_remove, name='cart_remove'),
    path('cart_update/<int:id>', views.cart_update, name='cart_update'),
    path('removeAll', views.removeAll, name='removeAll'),
    path('cart_detail', views.cart_detail, name='cart_detail'),
    path('checkoutDetail', views.checkoutDetail, name='checkoutDetail'),
    path('getValuesAccordingToSelectedCategory', views.getValuesAccordingToSelectedCategory, name='getValuesAccordingToSelectedCategory'),
    path('getSponsoshipValuesAccordingToSelectedCategory', views.getSponsoshipValuesAccordingToSelectedCategory, name='getSponsoshipValuesAccordingToSelectedCategory'),
    path('getCurrency', views.getCurrency, name='getCurrency'),
    path('generateActivationCode', views.generateActivationCode, name='generateActivationCode'),

    # REST APIS, URLS:
    path('api/register/', apis.register_view, name="apiRegister"),
    path('apiActivate/<uidb64>/<token>/', apis.ActivateAccount2.as_view(), name='apiActivate'),
    path('api/homePage/', apis.homePage, name='homePage'),
    path('api/externalProjects/', apis.externalProjects, name='externalProjects'),
    path('api/externalInitiative/', apis.externalInitiative, name='externalInitiative'),
    path('api/payZakat/', apis.payZakat, name='payZakat'),
    # path('api/dailySadaqa/', apis.dailySadaqa, name='dailySadaqa'),
    path('api/sponsorAFamily/', apis.sponsorAFamily, name='sponsorAFamily'),
    path('api/sponsorAnOrphan/', apis.sponsorAnOrphan, name='sponsorAnOrphan'),
    # FOR GETTING ALL SPONSORSHIP PROJECTS:
    path('api/sponsorships/', apis.sponsorships, name='sponsorships'),
    # GETTING THE SPONSORSHIPS PROJECTS WITH THE `POSTED` CATEGORY_ID:
    path('api/sponsorshipsAccordingToCategory/<int:categoryId>/', apis.sponsorshipsAccordingToCategory, name='sponsorshipsAccordingToCategory'),
    path('api/profile2/', apis.profile2, name='profile2'),

)

# urlpatterns += i18n_patterns[
#
#
# ]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
