from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    rating = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    visit_fee = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True) 

    def __str__(self):
        return self.name

class DoctorDetail(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='detail')
    about = models.TextField(verbose_name="about doctor", blank=True, null=True)

    def __str__(self):
        return f"جزئیات {self.doctor.name}"

