from django.urls import path
from . import views

urlpatterns = [
    path('criar-pesagem/', views.criar_pesagem, name='criar_pesagem'),
    path('pesagens-por-mes/', views.exibir_pesagem_por_mes, name='exibir_pesagem_por_mes'),
    path('quantidade_em_toneladas/', views.quantidade_de_toneladas_pesadas, name='quantidade_em_toneladas'),
    path('quantidade_catatreco/', views.pesagens_cata_treco, name='quantidade_catatreco'),
    path('pesagens_seletiva/', views.pesagens_seletiva, name='pesagens_seletiva'),
    path('meta-batida/', views.meta_batida, name='meta_batida'),
    path('ranking_cooperativas/', views.top_5_coperativas_por_pesagem, name='ranking_cooperativas'),
    path('eficiencia_motorista/', views.eficiencia_motoristas, name='eficiencia_motorista'),
    path('pesagem_por_tipo_mes/', views.pesagens_ao_longo_ano_por_tipo_pesagem, name='tipos_pesagem_frequentes'),
    path('eficiencia_veiculo/', views.eficiencia_veiculos, name='eficiencia_veiculo'),
    path('eficiencia_cooperativas/', views.eficiencia_cooperativas, name='eficiencia_cooperativas'),
]
