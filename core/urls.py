from django.contrib import admin
from django.urls import path, include
from receipt.views import NotasUpdateView
from django.contrib.auth import views as auth_views

from transport.views import DashboardView  

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
    path("cards/", DashboardView.as_view(), name="cards"),
    # Autenticação
    path("accounts/", include("django.contrib.auth.urls")),
]
