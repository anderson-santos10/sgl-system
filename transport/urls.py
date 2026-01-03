from django.urls import path
from .views import CriarTransporteView, CenarioTransporteView, EditarTransporteView

app_name = "transport"

urlpatterns = [
    path("criar/", CriarTransporteView.as_view(), name="criar_transporte"),
    path("editar/<int:pk>/", EditarTransporteView.as_view(), name="editar_transporte"),
    path("cenario/", CenarioTransporteView.as_view(), name="cenario_transporte"),    
]
