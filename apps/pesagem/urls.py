from django.urls import path
from . import views

urlpatterns = [
    path('criar-pesagem/', views.criar_pesagem, name='criar_pesagem'),
    path('pesagens-por-mes/', views.exibir_pesagem_por_mes, name='exibir_pesagem_por_mes'),
    path('meta-batida/', views.meta_batida, name='meta_batida'),
    path('ranking_cooperativas/', views.top_5_coperativas_por_pesagem, name='ranking_cooperativas'),
    path('eficienica_motorista/', views.eficiencia_motoristas, name='eficiencia_motorista'),
    path('pesagem_por_tipo_mes/', views.def_pesagens_ao_longo_ano_por_tipo_pesagem, name='tipos_pesagem_frequentes'),
    path('eficiencia_veiculos/', views.eficiencia_veiculos, name='tipos_pesagem_frequentes'),
    path('eficiencia_cooperativas/', views.eficiencia_cooperativas, name='tipos_pesagem_frequentes'),


]
