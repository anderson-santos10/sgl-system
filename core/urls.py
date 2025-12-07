from django.contrib import admin
from django.urls import path, include
from receipt.views import DashboardView, NotasUpdateView
from expedicao.views import CargaUpdateView, CargaDeleteView
from django.contrib.auth import views as auth_views  

urlpatterns = [
    path("admin/", admin.site.urls),

    # Raiz do site vai direto para o login
    path("", auth_views.LoginView.as_view(template_name="registration/login.html"), name="root_login"),

    # Apps
    path("receipt/", include("receipt.urls")),   
    path("expedicao/", include(('expedicao.urls', 'expedicao'), namespace='expedicao')),
    path("transport/", include(('transport.urls', 'transport'), namespace='transport')),

    # Views diretas
    path("update/<int:pk>", NotasUpdateView.as_view(), name="notas_update"),
    path("update_cargas/<int:pk>", CargaUpdateView.as_view(), name="editar_carga"),
    path("delete/<int:pk>", CargaDeleteView.as_view(), name="excluir_carga"),
    path("pg_inicial/", DashboardView.as_view(), name="pg_inicial"),

    # Autenticação
    path("accounts/", include("django.contrib.auth.urls")),
]
