from rest_framework import serializers
from .models import Veiculo

class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        fields = ['id', 'prefixo', 'tipo', 'placa_veiculo', 'em_manutencao']
    def validate_tipo(self, value):
        tipos_validos = [opcao[0] for opcao in Veiculo.TIPOS_VEICULO]
        if value not in tipos_validos:
            raise serializers.ValidationError(f"Tipo inválido. Valores permitidos: {tipos_validos}")
        return value
    def validate_em_manutencao(self, value):
        if value not in ['SIM', 'NÃO']:
            raise serializers.ValidationError("o campo 'em_manutencao' deve ser 'SIM' ou 'NÃO'.")
        return value
