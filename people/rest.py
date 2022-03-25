from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import People
from django.views.decorators.csrf import csrf_exempt
from .serializers import PeopleSerializer


class CreatePeople(APIView):
    authentication_classes = []
    permission_classes = []

    @csrf_exempt
    def post(self, request):
        name = request.data.get('name', None)
        phone = request.data.get('phone', None)
        if phone is not None:
            try:
                p = People.objects.get(phone=phone)
            except People.DoesNotExist:
                p = None
            if p is None:
                person = People.objects.create(
                    name=name, phone=phone)
                se = PeopleSerializer(instance=person)
                return Response(se.data)
            else:
                return Response({'error': "Phone number already exists"},
                                status=status.HTTP_400_BAD_REQUEST,)