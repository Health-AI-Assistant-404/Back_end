from rest_framework import serializers
from .models import Doctor, DoctorDetail

class DoctorSerializer(serializers.ModelSerializer):
    visit_fee = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True) 

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'specialty', 'location', 'image', 'rating', 'visit_fee']

    def get_visit_fee(self, obj):
        return f"{int(obj.visit_fee):,}"


class DoctorDetailSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = DoctorDetail
        fields = ['id', 'doctor', 'about']
