from django.urls import path
from . import views


urlpatterns = [
    path('doctors-list/',  views.doctor_list ),
    path('doctors-details/',  views.doctor_details ),
    path("scrape/<str:city_name>", views.get_city_doctors),
    path("redirect/doctor/<slug:slug>/<str:doctor_id>/", views.doctor_redirect, name="doctor_redirect"),
    
]