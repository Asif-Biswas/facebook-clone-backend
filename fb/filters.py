from .models import User, Group
import django_filters
from django.db import models

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        filter_overrides = {
             models.CharField: {
                 'filter_class': django_filters.CharFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'icontains',
                 },
             },
             models.BooleanField: {
                 'filter_class': django_filters.BooleanFilter,
                 'extra': lambda f: {
                     'widget': forms.CheckboxInput,
                 },
             },
         }

class GroupFilter(django_filters.FilterSet):
    class Meta:
        model = Group
        fields = ['name']
        filter_overrides = {
             models.CharField: {
                 'filter_class': django_filters.CharFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'icontains',
                 },
             },
         }
