from django.http import JsonResponse
from django.urls import path, include

def home_view(request):
    return JsonResponse({'message': 'Welcome to HealthAI API. Use /api/ endpoints to interact.'})

urlpatterns = [
    path('', home_view), 
    path('api/', include('account.urls')),  ]
