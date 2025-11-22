from django.urls import path
from . import views


urlpatterns = [
    path('doctors-list/',  views.doctor_list ),
    path('doctors-details/',  views.doctor_details ),
    
]