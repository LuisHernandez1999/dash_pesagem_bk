from rest_framework import serializers
from .models import Cooperativa

class CooperativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperativa
        fields = ['id', 'nome']
