from django.shortcuts import redirect
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

from doctors.utils import get_build_id
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

@api_view(["GET"])
def get_city_doctors(request, city_name):
    try:
        build_id = get_build_id()
        if not build_id:
            return Response({"error": "Build ID not found"}, status=500)

        url = f"https://doctoreto.com/_next/data/{build_id}/city/{city_name}.json"
        response = requests.get(url).json()

        dehydrated = response.get("pageProps", {}) \
                             .get("dehydratedState", {}) \
                             .get("queries", [])

        doctors = []

        for q in dehydrated:
            items = q.get("state", {}).get("data", [])
            if isinstance(items, list):
                for doc in items:
                    doctors.append({
                        "id": doc.get("id"),
                        "slug": doc.get("slug"),
                        "fullName": doc.get("fullName"),
                        "title": doc.get("title"),
                        "rate": doc.get("rate"),
                        "medicalNumber": doc.get("medicalNumber"),
                    })

        return Response({"count": len(doctors), "doctors": doctors})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(["GET"])
def doctor_redirect(request, slug, doctor_id):
    
    target_url = f"https://doctoreto.com/doctor/{slug}/{doctor_id}?searchedFrom=headerKeyword"
    return redirect(target_url)