from rest_framework import serializers
from .models import Pesagem
from apps.colaborador.models import Colaborador
from apps.veiculo.models import Veiculo
from apps.coperativa.models import Cooperativa


class PesagemSerializer(serializers.ModelSerializer):
    colaborador_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Colaborador.objects.all()
    )
    prefixo_id = serializers.PrimaryKeyRelatedField(
        queryset=Veiculo.objects.all()
    )
    cooperativa_id = serializers.PrimaryKeyRelatedField(
        queryset=Cooperativa.objects.all()
    )
    motorista_id = serializers.PrimaryKeyRelatedField(
        queryset=Colaborador.objects.all()
    )
    peso_calculado = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        read_only=True
    )

    class Meta:
        model = Pesagem
        fields = [
            'id',
            'data',
            'prefixo_id',
            'colaborador_id',
            'cooperativa_id',
            'responsavel_coop',
            'motorista_id',
            'hora_chegada',
            'hora_saida',
            'numero_doc',
            'volume_carga',
            'tipo_pesagem',
            'peso_calculado'
        ]
