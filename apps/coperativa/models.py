from django.db import models


class Cooperativa(models.Model):
    
    nome = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'cooperativa'
        
    def __str__(self):
        return self.nome
    