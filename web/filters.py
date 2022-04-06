from projects.models import Project, Category
import django_filters
from django import forms
from django.forms import ModelForm, TextInput, EmailInput


class ProjectFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr='icontains')
    # location = django_filters.CharFilter(lookup_expr='icontains')
    # total_amount__lte = django_filters.NumberFilter(name='total_amount', lookup_expr='total_amount__lte')
    # total_amount__gte = django_filters.NumberFilter(name='total_amount', lookup_expr='total_amount__gte')

    CHOICES = [('True', 'نعم'), ('False', 'ل')]
    isZakat = django_filters.CharFilter(label='Zakat', widget=forms.RadioSelect(choices=CHOICES))

    class Meta:
        model = Project
        fields = ['name', 'location', 'total_amount', 'isZakat', 'category']
