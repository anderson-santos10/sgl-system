from django.urls import include, path
from .views import CriarTransporteView, CenarioTransporteView, DashboardView, EditarTransporteView

app_name = "transport"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("criar/", CriarTransporteView.as_view(), name="criar_transporte"),
    path("editar/<int:pk>/", EditarTransporteView.as_view(), name="editar_transporte"),
    path("cenario/", CenarioTransporteView.as_view(), name="cenario_transporte"),    
]
