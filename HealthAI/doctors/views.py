from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Doctor , DoctorDetail
from .serializers import DoctorSerializer , DoctorDetailSerializer

@api_view(['GET'])
def doctor_list(request):
    
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def doctor_details(request):
    
    doctor_details_list = DoctorDetail.objects.all()
    serializer = DoctorDetailSerializer(doctor_details_list, many=True)

    return Response(serializer.data)