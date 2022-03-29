import pyrebase
from django.contrib import admin
from django.forms import BaseInlineFormSet
from import_export import resources
from import_export.admin import ExportMixin
from import_export.admin import ImportExportActionModelAdmin
from rangefilter.filter import DateRangeFilter
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.contrib import messages

from .models import Category, Project, Donate, Transaction, \
    TransactionKNETMachine, TransactionCash, ProjectsDirectory, SMS, Country, Sacrifice, sponsorship, \
    sponsorshipProjects, sponsorshipPageContent, CompaignCategory, Compaigns, CustomerIds, DonateSponsor, volunteer, partner, ProjectPDF, PostImage

config = {
    "apiKey": "553f4037184cf18490885a33458dc1cdce96b642",
    "authDomain": "basaier-8a7fe.firebaseapp.com",
    "databaseURL": "https://basaier-8a7fe.firebaseio.com",
    "storageBucket": "basaier-8a7fe.appspot.com"
}

firebase = pyrebase.initialize_app(config)


# class NotificationsAdmin(admin.ModelAdmin):
#     model = Notifications
#     list_display = ('id', 'compaignId', 'compaignId__projectName', 'compaignId__is_active')
#     list_filter = (
#         ('compaignId', admin.RelatedOnlyFieldListFilter),
#         'compaignId__projectName', 'compaignId__is_active'
#     )
#     def compaignId__projectName(self, instance):
#         return instance.compaignId.projectName
#
#     def compaignId__is_active(self, instance):
#         return instance.compaignId.is_active


class CustomerIdsAdmin(admin.ModelAdmin):
    model = CustomerIds
    list_display = ['customer_id', 'object_customer', 'live_mode', 'api_version', 'first_name', 'last_name', 'email',
                    'phone', 'description', 'currency', 'title', 'nationality']


# class CompaignsAdmin(admin.ModelAdmin):
#     model = Compaigns
#     list_display = ['nameOfDeceased', 'projectName', 'is_active', 'detail', 'created_at', 'getCategories', 'user']
#     list_editable = ['is_active']
#     actions = ['enable_selected', 'disable_selected']
#     ordering = ['-created_at']
#
#     def getCategories(self, obj):
#         return "\n".join([p.name for p in obj.compaignCategory.all()])
#
#     def enable_selected(self, request, queryset):
#         queryset.update(is_active=True)
#
#     def disable_selected(self, request, queryset):
#         queryset.update(is_active=False)
#
#     enable_selected.short_description = "Activate"
#     disable_selected.short_description = "Disable"


class DonateResource(resources.ModelResource):
    class Meta:
        model = Donate
        fields = (
            'id', 'transaction__id', 'amount', 'project__donater_name', 'project__donater_phone', 'email',
            'project__name', 'category__name', 'transaction__payment_method',
            'transaction__status', 'created_at', 'description')


class DonateAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = DonateResource
    model = Donate
    actions = None
    list_display = (
        'id', 'user_id', 'project_id', 'category', 'transaction_id', 'amount',
        'email',
        'project_name', 'description', 'payment_method', 'project_donater_name', 'project_donater_phone',
        'status', 'created_at')

    list_filter = (
        ('created_at', DateRangeFilter),
        ('project__is_hidden', admin.ChoicesFieldListFilter),
        ('project', admin.RelatedOnlyFieldListFilter),
        ('transaction__status', admin.ChoicesFieldListFilter),
        ('transaction__payment_method', admin.ChoicesFieldListFilter),
    )

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(DonateAdmin, self).change_view(
            request, object_id, extra_context=extra_context)


class DonateInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super(DonateInlineFormSet, self).save_new(form, commit=commit)
        if obj.project.id == 79:
            # project = Project.objects.get(pk=4)
            # db = firebase.database()
            # data = {"total_funded": float(obj.project.total_funded())}
            # db.child("donates").push(data)
            return obj

        return obj

    def save_existing(self, form, instance, commit=True):
        return form.save(commit=commit)


class DonateInlineAdmin(admin.StackedInline):
    model = Donate
    formset = DonateInlineFormSet
    extra = 0
    exclude = ('user', 'email')


# DONATE SPONSOR:
class DonateSponsorResource(resources.ModelResource):
    class Meta:
        model = DonateSponsor
        fields = (
            'id', 'transaction__id', 'amount', 'email',
            'sponsorProject__name', 'sponsorCategory__category', 'transaction__payment_method',
            'transaction__status', 'created_at', 'description')


class DonateSponsorAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = DonateSponsorResource
    model = Donate
    actions = None
    list_display = (
        'id', 'user_id', 'project_id', 'sponsorCategory', 'sponsorProject', 'transaction_id2', 'amount',
        'email',
        'project_name2', 'description', 'payment_method2',
        'status2', 'created_at')

    list_filter = (
        ('created_at', DateRangeFilter),
        ('project', admin.RelatedOnlyFieldListFilter),
        ('transaction__status', admin.ChoicesFieldListFilter),
        ('transaction__payment_method', admin.ChoicesFieldListFilter),
    )

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(DonateSponsorAdmin, self).change_view(
            request, object_id, extra_context=extra_context)


class DonateSponsorInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super(DonateSponsorInlineFormSet, self).save_new(form, commit=commit)
        if obj.project.id == 79:
            # project = Project.objects.get(pk=4)
            # db = firebase.database()
            # data = {"total_funded": float(obj.project.total_funded())}
            # db.child("donates").push(data)
            return obj

        return obj

    def save_existing(self, form, instance, commit=True):
        return form.save(commit=commit)


class DonateSponsorInlineAdmin(admin.StackedInline):
    model = DonateSponsor
    formset = DonateSponsorInlineFormSet
    extra = 0
    exclude = ('user', 'email')


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    actions = None
    list_display = ('payment_method', 'status', 'knet_payment_id', 'result',
                    'auth_code', 'reference', 'trans_id', 'post_date', 'tap_id',
                    'total_donation')
    list_filter = (
        ('status', admin.ChoicesFieldListFilter),
    )

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(TransactionAdmin, self).change_view(
            request, object_id, extra_context=extra_context)


class TransactionKNETMachineAdmin(admin.ModelAdmin):
    model = Transaction
    actions = None
    inlines = [DonateInlineAdmin, ]
    list_display = ('id', 'payment_method', 'status', 'knet_payment_id',
                    'result', 'auth_code', 'reference', 'trans_id',
                    'post_date', 'total_donation')
    exclude = ('payment_method', 'status', 'result')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, *args, **kwargs):
        self.exclude = getattr(self, 'exclude', ())
        return super(TransactionKNETMachineAdmin,
                     self).change_view(*args, **kwargs)

    def get_queryset(self, request):
        my_queryset = Transaction.objects.filter(payment_method='Knet_machine')
        return my_queryset

    def add_view(self, *args, **kwargs):
        self.exclude = getattr(self, 'exclude', ())
        return super(TransactionKNETMachineAdmin,
                     self).add_view(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.payment_method = 'Knet_machine'
        obj.status = 'Approved'
        obj.result = 'CAPTURED'
        super(TransactionKNETMachineAdmin,
              self).save_model(request, obj, form, change)


class TransactionCashAdmin(admin.ModelAdmin):
    model = Transaction
    actions = None
    inlines = [DonateInlineAdmin, ]
    list_display = ('id', 'payment_method', 'status', 'knet_payment_id',
                    'result', 'auth_code', 'reference', 'trans_id',
                    'post_date', 'total_donation')
    exclude = (
        'payment_method', 'status', 'result', 'post_date', 'total_donation', 'auth_code', 'trans_id', 'knet_payment_id')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def change_view(self, *args, **kwargs):
        self.exclude = getattr(self, 'exclude', ())
        return super(TransactionCashAdmin,
                     self).change_view(*args, **kwargs)

    def get_queryset(self, request):
        my_queryset = Transaction.objects.filter(payment_method='Cash')
        return my_queryset

    def add_view(self, *args, **kwargs):
        self.exclude = getattr(self, 'exclude', ())
        return super(TransactionCashAdmin,
                     self).add_view(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.payment_method = 'Cash'
        obj.status = 'Approved'
        obj.result = 'CAPTURED'
        super(TransactionCashAdmin,
              self).save_model(request, obj, form, change)


# @admin.register(Project)
# class ProjectAdmin(ImportExportModelAdmin):
#     pass
class PostImageAdmin(admin.StackedInline):
    model = PostImage


class ProjectAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    inlines = [PostImageAdmin]
    list_display = (
        '__str__', 'total_amount', 'active_compaign', 'is_hidden', 'total_funded', 'total_efunded', "total_efunded_per_category",
        'is_closed',
        'created_at')

    list_filter = (
        ('is_hidden'),
        ('is_closed'),
        ('is_compaign'),
        ('is_thawab'),
        ('isZakat'),
        ('category'),
    )
    list_editable = ['active_compaign', 'is_hidden']
    search_fields = ['name', 'nameEn']
    readonly_fields = ('created_at', 'created_by',)

    class Meta:
        model = Project


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    pass
# limitCount = CompaignCategory.projectsLimit
#
#
# class CompaignsAdmin(admin.ModelAdmin):
#     def add_view(self, request, form_url='', extra_context=None):
#         if self.model.objects.count() >= limitCount:
#             self.message_user(request, 'Project Limit Has Been Reached, You Cannot Add More.', messages.ERROR)
#             return HttpResponseRedirect(reverse(f'admin:{self.model._meta.app_label}_about_changelist'))
#         return super().add_view(request, form_url, extra_context)


admin.site.register(SMS)
admin.site.register(ProjectsDirectory)
admin.site.register(Category)
admin.site.register(Country)
admin.site.register(Sacrifice)
admin.site.register(volunteer)
admin.site.register(partner)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectPDF)
admin.site.register(TransactionKNETMachine, TransactionKNETMachineAdmin)
admin.site.register(TransactionCash, TransactionCashAdmin)

admin.site.register(Donate, DonateAdmin)
admin.site.register(DonateSponsor, DonateSponsorAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(sponsorship)
admin.site.register(sponsorshipProjects)
admin.site.register(sponsorshipPageContent)
# admin.site.register(giftCategories)
# admin.site.register(gifts)
# admin.site.register(CompaignCategory)
# admin.site.register(Compaigns, CompaignsAdmin)
admin.site.register(CustomerIds, CustomerIdsAdmin)
# admin.site.register(Notifications, NotificationsAdmin)

# admin.site.register(Donate)
# admin.site.register(Transaction)
