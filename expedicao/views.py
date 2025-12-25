from django.views.generic import ListView
from transport.models import Lecom

class CenarioExpedicaoView(ListView):
    model = Lecom
    template_name = "expedicao/cenario_expedicao.html"
    context_object_name = "lecoms"
    ordering = ["-id"]

    def get_queryset(self):
        # Retorna apenas LECOMs LIBERADAS
        queryset = (
            super()
            .get_queryset()
            .prefetch_related("cargas", "veiculo")
            .filter(status="LIBERADO")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Monta grupo_cargas só com LECOMs liberadas
        grupo_cargas = []
        for lecom in context["lecoms"]:
            grupo_cargas.append({
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq")
            })

        context["grupo_cargas"] = grupo_cargas
        context["total_lecoms"] = context["lecoms"].count()
        return context
