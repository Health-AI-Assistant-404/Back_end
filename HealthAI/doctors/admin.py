from django.contrib import admin
from django import forms
from .models import Doctor, DoctorDetail
 
# Register your models here.

class DoctorAdminForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'rating': forms.NumberInput(attrs={'step': 0.1, 'min': 0, 'max': 5}),
        }

class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(DoctorDetail)