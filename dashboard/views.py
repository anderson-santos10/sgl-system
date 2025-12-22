from django.shortcuts import render
from django.views import View
from .utils import get_context_recebimento, get_context_transporte
from datetime import date

class HomeDashboardView(View):
    template_name = "dashboard/home.html"

    def get(self, request):
        # Contexto base
        context = {"hoje": date.today()}

        # Adiciona os dados de recebimento e transporte
        context.update(get_context_recebimento())
        context.update(get_context_transporte())

        return render(request, self.template_name, context)
