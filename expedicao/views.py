from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from transport.models import Lecom
from expedicao.models import ControleSeparacao, SeparacaoCarga
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class CenarioExpedicaoView(LoginRequiredMixin, ListView):
    model = Lecom
    template_name = "expedicao/cenario_expedicao.html"
    context_object_name = "lecoms"
    ordering = ["-id"]
    login_url = "/accounts/login/"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(status="LIBERADO")
            .select_related("veiculo")
            .prefetch_related("cargas")
        )

        # filtros
        data = self.request.GET.get("data")
        lecom = self.request.GET.get("lecom")
        destino = self.request.GET.get("destino")
        veiculo = self.request.GET.get("veiculo")

        if data:
            queryset = queryset.filter(data=data)

        if lecom:
            queryset = queryset.filter(lecom__icontains=lecom)

        if destino:
            queryset = queryset.filter(destino__icontains=destino)

        if veiculo:
            queryset = queryset.filter(veiculo__tipo_veiculo=veiculo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["grupo_cargas"] = [
            {
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq")
            }
            for lecom in context["lecoms"]
        ]

        context["total_lecoms"] = context["lecoms"].count()
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

class CenarioSeparacaoView(LoginRequiredMixin, View):
    template_name = "expedicao/cenario_separacao.html"

    def get(self, request):
        separacoes = (
            ControleSeparacao.objects
            .filter(liberada=True)
            .select_related("lecom", "lecom__veiculo")
            .prefetch_related("cargas", "cargas__carga")
            .order_by("-criado_em")
        )

        return render(request, self.template_name, {
            "separacoes": separacoes
        })
        
class DetalheCardView(LoginRequiredMixin, View):
    template_name = "expedicao/detalhe_carga.html"

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)

        return render(request, self.template_name, {
            "lecom": lecom,
            "cargas": lecom.cargas.all().order_by("seq"),
        })

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)

        # evita duplicação
        if hasattr(lecom, "controle_separacao"):
            messages.warning(
                request,
                "Este transporte já possui separação criada."
            )
            return redirect("expedicao:cenario_separacao")

        # cria controle (NÃO liberado ainda)
        controle = ControleSeparacao.objects.create(
            lecom=lecom
        )

        # cria as cargas da separação
        for carga in lecom.cargas.all():
            SeparacaoCarga.objects.create(
                controle=controle,
                carga=carga,
                seq=carga.seq or 1,
                numero_transporte=carga.carga,
                entregas=carga.total_entregas,
                mod=carga.mod,
            )

        # 🔥 LIBERAÇÃO OFICIAL
        controle.liberar_separacao()

        messages.success(
            request,
            "Separação criada e liberada com sucesso."
        )

        return redirect("expedicao:cenario_separacao")

class CenarioCarregamentoView(LoginRequiredMixin, View):
    template_name = "expedicao/cenario_carregamento.html"

    def get(self, request, controle_id):
        controle = get_object_or_404(
            ControleSeparacao,
            pk=controle_id,
            liberada=True
        )

        return render(request, self.template_name, {
            "controle": controle,
            "cargas": controle.cargas.all()
        })
