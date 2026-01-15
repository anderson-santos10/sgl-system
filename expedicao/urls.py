from django.urls import path
from .views import (CenarioExpedicaoView, CenarioCardSeparacaoView,
                    DetalheCardView, CenarioSeparacaoView, CenarioCarregamentoView)

app_name = "expedicao"

urlpatterns = [
    path('cenario_expedicao/', CenarioExpedicaoView.as_view(), name = "cenario_expedicao"),
    path("cenario_card_separacao/<int:pk>/", CenarioCardSeparacaoView.as_view(), name="cenario_card_separacao"),
    path('detalhe/<int:pk>/', DetalheCardView.as_view(), name = "detalhe_card"),
    path("separacao/", CenarioSeparacaoView.as_view(),name="cenario_separacao"),
    path('cenario/carregamento/<int:controle_id>/', CenarioCarregamentoView.as_view(), name='cenario_carregamento'),
    

]
