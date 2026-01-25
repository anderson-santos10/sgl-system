from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from transport.models import Carga, Lecom, Veiculo
from expedicao.models import ControleSeparacao, SeparacaoCarga
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
            .select_related(
                "veiculo",
                "controle_separacao", 
            )
            .prefetch_related("cargas")
        )

        data = self.request.GET.get("data")
        lecom = self.request.GET.get("lecom")
        destino = self.request.GET.get("destino")
        veiculo = self.request.GET.get("veiculo")
        controle_id = self.request.GET.get("controle_id")
        carga = self.request.GET.get("carga")

        if controle_id and controle_id.isdigit():
            queryset = queryset.filter(id=int(controle_id))

        if data:
            queryset = queryset.filter(data=data)

        if lecom:
            queryset = queryset.filter(lecom__icontains=lecom)

        if destino:
            queryset = queryset.filter(destino__icontains=destino)

        if veiculo:
            queryset = queryset.filter(veiculo__tipo_veiculo=veiculo)

        if carga:
            queryset = queryset.filter(cargas__carga__icontains=carga).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["veiculos"] = Veiculo.TIPO_VEICULO_CHOICES
        context["grupo_cargas"] = [
            {
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq"),
            }
            for lecom in context["lecoms"]
        ]
        context["total_lecoms"] = context["lecoms"].count()
        context["filtro_data"] = self.request.GET.get("data", "")

        return context


class CenarioSeparacaoView(LoginRequiredMixin, ListView):
    template_name = "expedicao/cenario_separacao.html"
    context_object_name = "grupo_cargas"
    login_url = "/accounts/login/"

    def get_queryset(self):
        queryset = (
            ControleSeparacao.objects
            .select_related("lecom", "lecom__veiculo")
            .prefetch_related("cargas")
            .filter(status__in=[
                ControleSeparacao.STATUS_AGUARDANDO,
                ControleSeparacao.STATUS_EM_ANDAMENTO,
                ControleSeparacao.STATUS_CONCLUIDO,
            ])
            .order_by("-criado_em")
        )

        filtros = {
            "controle_id": self.request.GET.get("controle_id"),
            "data": self.request.GET.get("data"),
            "lecom": self.request.GET.get("lecom"),
            "destino": self.request.GET.get("destino"),
            "veiculo": self.request.GET.get("veiculo"),
            "carga": self.request.GET.get("carga"),
            "status": self.request.GET.get("status"),
        }

        if filtros["controle_id"] and filtros["controle_id"].isdigit():
            queryset = queryset.filter(pk=int(filtros["controle_id"]))

        if filtros["data"]:
            queryset = queryset.filter(lecom__data=filtros["data"])

        if filtros["lecom"]:
            queryset = queryset.filter(lecom__lecom__icontains=filtros["lecom"])

        if filtros["destino"]:
            queryset = queryset.filter(lecom__destino__icontains=filtros["destino"])

        if filtros["veiculo"]:
            queryset = queryset.filter(lecom__veiculo__tipo_veiculo=filtros["veiculo"])

        if filtros["carga"]:
            queryset = queryset.filter(
                cargas__numero_transporte__icontains=filtros["carga"]
            ).distinct()

        if filtros["status"]:
            queryset = queryset.filter(status=filtros["status"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["grupo_cargas"] = [
            {
                "grupo": controle,
                "cargas": controle.cargas.all().order_by("seq"),
            }
            for controle in context["grupo_cargas"]
        ]

        context["veiculos"] = Veiculo.TIPO_VEICULO_CHOICES

        return context

    def post(self, request, *args, **kwargs):
        controle_id = request.POST.get("controle_id")

        if controle_id:
            controle = get_object_or_404(ControleSeparacao, pk=controle_id)
            controle.status = ControleSeparacao.STATUS_EM_ANDAMENTO
            controle.save()

        return redirect("expedicao:cenario_separacao")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["grupo_cargas"] = [
            {
                "grupo": controle,
                "cargas": controle.cargas.all().order_by("seq"),
            }
            for controle in context["grupo_cargas"]
        ]

        context["veiculos"] = Veiculo.TIPO_VEICULO_CHOICES
        

        return context


class DetalheCardView(LoginRequiredMixin, View):
    template_name = "expedicao/detalhe_carga.html"

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)

        return render(
            request,
            self.template_name,
            {
                "lecom": lecom,
                "cargas": lecom.cargas.all().order_by("seq"),
            },
        )

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        controle = getattr(lecom, "controle_separacao", None)

        if not controle:
            controle = ControleSeparacao.objects.create(lecom=lecom)

            for carga in lecom.cargas.all():
                SeparacaoCarga.objects.create(
                    controle=controle,
                    carga=carga,
                    seq=carga.seq or 1,
                    numero_transporte=carga.carga,
                    entregas=carga.total_entregas,
                    mod=carga.mod,
                )

        if controle.status == ControleSeparacao.STATUS_PENDENTE:
            controle.liberar_separacao() 

            messages.success(
                request,
                "Separação liberada e enviada para o cenário.",
            )
        else:
            messages.warning(
                request,
                "Esta separação já foi liberada.",
            )

        return redirect("expedicao:cenario_separacao")



class CenarioCarregamentoView(LoginRequiredMixin, View):
    template_name = "expedicao/cenario_carregamento.html"

    def get(self, request, controle_id):
        controle = get_object_or_404(
            ControleSeparacao,
            pk=controle_id,
            status__in=[
                ControleSeparacao.STATUS_EM_ANDAMENTO,
                ControleSeparacao.STATUS_CONCLUIDO,
            ],
        )

        return render(
            request,
            self.template_name,
            {
                "controle": controle,
                "cargas": controle.cargas.all(),
            },
        )


class EditarSeparacaoView(LoginRequiredMixin, View):
    template_name = "expedicao/editar_separacao.html"

    def get(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)
        separacao = SeparacaoCarga.objects.filter(controle=controle).first()

        return render(
            request,
            self.template_name,
            {
                "controle": controle,
                "lecom": controle.lecom,
                "cargas": controle.cargas.all(),
                "separacao": separacao,
            },
        )

    def post(self, request, pk):
        controle = get_object_or_404(ControleSeparacao, pk=pk)
        separacao = SeparacaoCarga.objects.filter(controle=controle).first()

        try:
            with transaction.atomic():
                controle.resumo_conf = bool(request.POST.get("resumo_conf"))
                controle.resumo_motorista = bool(request.POST.get("resumo_motorista"))
                controle.etiquetas_cds = bool(request.POST.get("etiquetas_cds"))
                controle.carga_gerada = bool(request.POST.get("carga_gerada"))
                controle.save()

                if separacao:
                    separacao.ot = request.POST.get("ot", "").strip()
                    separacao.atribuida = bool(request.POST.get("atribuida"))
                    separacao.finalizada = bool(request.POST.get("finalizada"))
                    separacao.save()

        except Exception as e:
            messages.error(request, f"Erro ao salvar separação: {e}")
            return redirect("expedicao:editar_separacao", pk=pk)

        messages.success(request, "Separação atualizada com sucesso.")
        return redirect("expedicao:editar_separacao", pk=pk)
