from django.db import models


class Colaborador(models.Model):
    TIPOS_FUNCAO = ['MOTORISTA', 'OPERADOR', 'COLETOR']
    TIPOS_TURNO = ['DIURNO', 'NOTURNO', 'VESPERTINO']
    TIPOS_STATUS = ['ATIVO', 'INATIVO']
    TIPOS_PA = ['PA1', 'PA2', 'PA3', 'PA4']
    
    nome = models.CharField(max_length=100)
    matricula = models.IntegerField(unique=True)
    funcao = models.CharField(max_length=9, choices=[(x, x) for x in TIPOS_FUNCAO])
    turno = models.CharField(max_length=10, choices=[(x, x) for x in TIPOS_TURNO])
    status = models.CharField(max_length=7, choices=[(x, x) for x in TIPOS_STATUS])
    pa = models.CharField(max_length=4, choices=[(x, x) for x in TIPOS_PA])
    
    
    class Meta:
        indexes =[
            models.Index(fields=['nome']),
            models.Index(fields=['matricula']),
            models.Index(fields=['funcao']),
            models.Index(fields=['pa']),
            models.Index(fields=['turno']),
        ]
        
        db_table = 'colaborador'
        
    def __str__(self):
        return f"{self.nome} - {self.matricula}"
    