from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from transport.models import Lecom
from expedicao.models import ControleSeparacao, SeparacaoCarga
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction

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

class CenarioSeparacaoView(LoginRequiredMixin, ListView):
    template_name = "expedicao/cenario_separacao.html"
    context_object_name = "separacoes"

    def get_queryset(self):
        return (
            ControleSeparacao.objects
            .select_related("lecom", "lecom__veiculo")
            .prefetch_related("cargas")
            .filter(
                liberada=True,
                status__in=["Aguardando", "Andamento"]
            )
            .order_by("-criado_em")
        )
        
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

        # tenta pegar o controle se já existir
        controle = getattr(lecom, "controle_separacao", None)

        # CASO 1: ainda NÃO existe controle

        if not controle:
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
                
        # CASO 2: existe mas ainda NÃO foi liberado

        if not controle.liberada:
            controle.liberar_separacao()

            messages.success(
                request,
                "Separação liberada e enviada para o cenário."
            )
        else:
            messages.warning(
                request,
                "Esta separação já está liberada."
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

class EditarSeparacaoView(View):
    template_name = "expedicao/editar_separacao.html"

    def get(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)

        # normalmente 1 separação por controle
        separacao = SeparacaoCarga.objects.filter(controle=controle).first()

        context = {
            "controle": controle,
            "lecom": controle.lecom,
            "cargas": controle.cargas.all(),
            "separacao": separacao,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)
        separacao = SeparacaoCarga.objects.filter(controle=controle).first()

        try:
            with transaction.atomic():

         
                # CONTROLE SEPARAÇÃO
                controle.resumo_conf = bool(request.POST.get("resumo_conf"))
                controle.resumo_motorista = bool(request.POST.get("resumo_motorista"))
                controle.etiquetas_cds = bool(request.POST.get("etiquetas_cds"))
                controle.carga_gerada = bool(request.POST.get("carga_gerada"))

                controle.save()

                # SEPARAÇÃO CARGA
                if separacao:
                    separacao.ot = request.POST.get("ot", "").strip()
                    separacao.atribuida = bool(request.POST.get("atribuida"))
                    separacao.finalizada = bool(request.POST.get("finalizada"))
                    separacao.conferente = request.POST.get(
                        "conferente", "Não informado"
                    ).strip()

                    separacao.save()

        except Exception as e:
            messages.error(request, f"Erro ao salvar separação: {e}")
            return redirect("expedicao:editar_separacao", pk=pk)

        messages.success(request, "Separação atualizada com sucesso.")
        return redirect("expedicao:editar_separacao", pk=pk)
