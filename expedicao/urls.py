from django.urls import path
from .views import (CenarioExpedicaoView, DetalheCardView, 
                    CenarioSeparacaoView, CenarioCarregamentoView, 
                    EditarSeparacaoView)

app_name = "expedicao"

urlpatterns = [
    path('cenario_expedicao/', CenarioExpedicaoView.as_view(), name = "cenario_expedicao"),
    path('detalhe/<int:pk>/', DetalheCardView.as_view(), name = "detalhe_card"),
    path("separacao/", CenarioSeparacaoView.as_view(),name="cenario_separacao"),
    path('cenario/carregamento/<int:controle_id>/', CenarioCarregamentoView.as_view(), name='cenario_carregamento'),
    path("separacao/editar/<int:pk>/",EditarSeparacaoView.as_view(),name="editar_carga")

    

]
