from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import LecomGroup, Transport
from .forms import TransportForm

class CenarioTransporteView(TemplateView):
    template_name = 'transport/cenario_transporte.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Busca todos os grupos ordenados
        grupos = LecomGroup.objects.all().order_by('lecom')
        transports = Transport.objects.all().order_by('lecom', 'seq')

        # Prepara uma lista de dicionários {grupo, cargas}
        grupo_cargas = []
        for grupo in grupos:
            cargas = transports.filter(lecom=grupo.lecom)
            grupo_cargas.append({
                'grupo': grupo,
                'cargas': cargas
            })

        context['grupo_cargas'] = grupo_cargas
        return context


class CenarioTransporteView(TemplateView):
    template_name = 'transport/cenario_transporte.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grupos = LecomGroup.objects.all().order_by('lecom')
        transports = Transport.objects.all().order_by('lecom', 'seq')

        grupo_cargas = []

        for grupo in grupos:
            # Filtra corretamente as cargas com o mesmo LECOM
            cargas = [c for c in transports if c.lecom == grupo.lecom]
            grupo_cargas.append({
                'grupo': grupo,
                'cargas': cargas
            })

        context['grupo_cargas'] = grupo_cargas
        return context
