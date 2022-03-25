from .models import People
from rest_framework import serializers


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = '__all__'
