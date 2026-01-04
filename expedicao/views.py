from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from transport.models import Lecom
from expedicao.models import ControleSeparacao
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class CenarioExpedicaoView(LoginRequiredMixin, ListView):
    model = Lecom
    template_name = "expedicao/cenario_expedicao.html"
    context_object_name = "lecoms"
    ordering = ["-id"]
    login_url = '/accounts/login/'


    def get_queryset(self):
        # Começa pegando todas LECOMs LIBERADAS
        queryset = (
            super()
            .get_queryset()
            .prefetch_related("cargas", "veiculo")
            .filter(status="LIBERADO")
        )

        # FILTRO POR DATA (se houver)
        transporte_id = self.request.GET.get("transporte_id")
        lecom = self.request.GET.get("lecom")
        status = self.request.GET.get("status")
        carga = self.request.GET.get("carga")
        veiculo = self.request.GET.get("veiculo")
        destino = self.request.GET.get("destino")
        data = self.request.GET.get("data")
        if data:
            queryset = queryset.filter(data=data)
            
        if transporte_id and transporte_id.isdigit():
            queryset = queryset.filter(id=int(transporte_id))
            
        if lecom:
            queryset = queryset.filter(lecom__icontains=lecom)
        
        if status in ["LIBERADO", "BLOQUEADO"]:
            queryset = queryset.filter(status=status)
            
            
        if carga:
            queryset = queryset.filter(
                cargas__carga__icontains=carga
            ).distinct()
            
        if veiculo:
            queryset = queryset.filter(
                veiculo__tipo_veiculo=veiculo
            )
            
        if destino:
            queryset = queryset.filter(
                destino__icontains=destino
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

        # Mantém o filtro de data no template
        context["filtro_data"] = self.request.GET.get("data", "")

        return context

class CenarioCardSeparacaoView(ListView):
    model = Lecom
    template_name = "expedicao/cenario_card_separacao.html"
    context_object_name = "lecoms"
    ordering = ["-id"]

    def get_queryset(self):
        # Retorna apenas LECOMs liberadas e faz prefetch para otimizar queries
        queryset = (
            super()
            .get_queryset()
            .filter(status="LIBERADO")
            .prefetch_related("cargas", "veiculo")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agrupa cargas por LECOM
        grupo_cargas = []
        for lecom in context["lecoms"]:
            grupo_cargas.append({
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq")
            })

        context["grupo_cargas"] = grupo_cargas
        context["total_lecoms"] = context["lecoms"].count()

        # Opcional: manter filtros, se tiver algum
        context["filtro_data"] = self.request.GET.get("data", "")
        context["filtro_lecom"] = self.request.GET.get("lecom", "")
        context["filtro_carga"] = self.request.GET.get("carga", "")
        context["filtro_veiculo"] = self.request.GET.get("veiculo", "")

        return context

class CenarioSeparacaoView(View):
    template_name = "expedicao/cenario_separacao.html"

    def get(self, request):
        separacoes = ControleSeparacao.objects.all().order_by("-id")

        return render(request, self.template_name, {
            "separacoes": separacoes
        })
        
class DetalheCard(View):
    template_name = "expedicao/detalhe_carga.html"

    def get(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)

        return render(request, self.template_name, {
            "controle": controle
        })

    def post(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)

        # =========================
        # CAMPOS EDITÁVEIS DA EXPEDIÇÃO
        # =========================
        controle.ot = request.POST.get("ot", "").strip()
        controle.outros_separadores = request.POST.get("outros_separadores", "").strip()
        controle.conferente = request.POST.get("conferente", "").strip()
        controle.observacao = request.POST.get("observacao", "").strip()

        # Status da separação (se existir no form)
        status = request.POST.get("status")
        if status:
            controle.status = status

        controle.save()

        # 🔁 REDIRECIONA PARA O CENÁRIO DE SEPARAÇÃO
        return redirect("expedicao:cenario_separacao")
    