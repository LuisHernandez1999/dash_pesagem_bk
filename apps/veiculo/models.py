from django.db import models

class Veiculo(models.Model):
    TIPOS_VEICULO = [
        ('Basculante', 'Basculante'),
        ('Selectolix', 'Selectolix'),
        ('Baú', 'Baú'),
    ]

    prefixo = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_VEICULO)
    placa_veiculo = models.CharField(max_length=8, blank=True, null=True, unique=True, verbose_name="Placa do Veículo")  # Novo campo
    em_manutencao = models.CharField(
        max_length=3,
        choices=[('SIM', 'Sim'), ('NÃO', 'Não')],
        default='NÃO',
        verbose_name="Em Manutenção"
    ) 

    class Meta:
        db_table = 'veiculo'

    def __str__(self):
        return f"{self.prefixo} - {self.tipo}"