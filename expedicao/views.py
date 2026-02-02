from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from transport.models import Lecom, Veiculo
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
            queryset = queryset.filter(
                cargas__carga__icontains=carga).distinct()

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
            ])
            .order_by("lecom_id")
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

        grupo_cargas = []
        for controle in context["grupo_cargas"]:
            cargas = controle.cargas.all().order_by("-seq")

            grupo_cargas.append({
                "grupo": controle,
                "cargas": cargas,
                "total_peso": controle.lecom.peso,  # pega do Lecom
                "total_m3": controle.lecom.m3,      # pega do Lecom
            })

        context["grupo_cargas"] = grupo_cargas
        context["veiculos"] = Veiculo.TIPO_VEICULO_CHOICES

        # totais gerais do cenário
        context["peso_total_cenario"] = sum(item["total_peso"] for item in grupo_cargas)
        context["m3_total_cenario"] = sum(item["total_m3"] for item in grupo_cargas)

        return context


class DetalheCardView(LoginRequiredMixin, View):
    model = Lecom
    template_name = "expedicao/analise_carga.html"
    context_object_name = "lecom"

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        cargas_transporte = lecom.cargas.all().order_by("seq")
        controle = getattr(lecom, "controle_separacao", None)

        total_peso_transporte = lecom.peso or 0
        total_m3_transporte = lecom.m3 or 0

        transportes_cenario = ControleSeparacao.objects.filter(
            status__in=[
                ControleSeparacao.STATUS_AGUARDANDO,
                ControleSeparacao.STATUS_EM_ANDAMENTO
            ]
        ).exclude(lecom=lecom).select_related("lecom")

        total_peso_cenario = sum(t.lecom.peso or 0 for t in transportes_cenario)
        total_m3_cenario = sum(t.lecom.m3 or 0 for t in transportes_cenario)

        total_peso_impacto = total_peso_cenario + total_peso_transporte
        total_m3_impacto = total_m3_cenario + total_m3_transporte

        context = {
            "controle": controle,
            "lecom": lecom,
            "cargas": cargas_transporte,
            "total_peso_transporte": total_peso_transporte,
            "total_m3_transporte": total_m3_transporte,
            "peso_total_cenario": total_peso_cenario,
            "m3_total_cenario": total_m3_cenario,
            "peso_total_impacto": total_peso_impacto,
            "m3_total_impacto": total_m3_impacto,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        controle = getattr(lecom, "controle_separacao", None)

        turno = request.POST.get("turno")
        data_carregamento = request.POST.get("data_carregamento")
        hora_carregamento = request.POST.get("hora_carregamento")

        # 🔹 SE NÃO EXISTE CONTROLE → CRIA
        if not controle:
            controle = ControleSeparacao.objects.create(
                lecom=lecom,
                turno=turno,
                data_carregamento=data_carregamento,
                hora_carregamento=hora_carregamento,
            )

            for carga in lecom.cargas.all():
                SeparacaoCarga.objects.create(
                    controle=controle,
                    carga=carga,
                    seq=carga.seq or 1,
                    numero_transporte=carga.carga,
                    entregas=carga.total_entregas,
                    mod=carga.mod,
                )

            controle.liberar_separacao()
            SeparacaoCarga.objects.filter(controle=controle).update(
                status=SeparacaoCarga.STATUS_AGUARDANDO
            )

            messages.success(request, f"Separação {lecom} liberada.")

        # 🔹 SE JÁ EXISTE → APENAS ATUALIZA
        else:
            controle.turno = turno
            controle.data_carregamento = data_carregamento
            controle.hora_carregamento = hora_carregamento
            controle.save()

            messages.success(request, f"Agendamento do transporte {lecom} atualizado.")

        return redirect("expedicao:cenario_separacao")



class CenarioCarregamentoView(LoginRequiredMixin, View):
    template_name = "expedicao/cenario_carregamento.html"

    def get(self, request):
        # Pega todas as cargas concluídas ou em andamento
        cargas = SeparacaoCarga.objects.filter(
            status__in=[
                SeparacaoCarga.STATUS_EM_ANDAMENTO,
                SeparacaoCarga.STATUS_CONCLUIDO,
            ]
        ).order_by('-inicio_separacao')  # mais recentes primeiro

        return render(request, self.template_name, {"cargas": cargas})


class EditarSeparacaoView(View):
    template_name = "expedicao/editar_separacao.html"

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        controle, _ = ControleSeparacao.objects.get_or_create(lecom=lecom)
        cargas = controle.cargas.all()  # todas as cargas do controle
        return render(request, self.template_name, {
            "controle": controle,
            "lecom": lecom,
            "cargas": cargas,
        })

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        controle = get_object_or_404(ControleSeparacao, lecom=lecom)
        carga_id = request.POST.get("carga_id")
        carga = get_object_or_404(SeparacaoCarga, id=carga_id, controle=controle)
        acao = request.POST.get("acao")

        try:
            with transaction.atomic():
                # =================== ATUALIZA CAMPOS DO FORMULÁRIO ===================
                carga.conferente = request.POST.get("Conferente", "").strip()
                carga.separadores = request.POST.get("Separadores", "").strip()
                carga.ot = request.POST.get("OT", "").strip()
                carga.box = request.POST.get("BOX", "").strip()
                carga.resumo_conf = bool(request.POST.get("resumo_conf"))
                carga.resumo_motorista = bool(request.POST.get("resumo_motorista"))
                carga.etiquetas_cds = bool(request.POST.get("etiquetas_cds"))
                carga.carga_gerada = bool(request.POST.get("carga_gerada"))

                # =================== INICIAR CARGA ===================
                if acao == "iniciar" and carga.status == carga.STATUS_AGUARDANDO:
                    carga.status = carga.STATUS_EM_ANDAMENTO
                    controle.status = controle.STATUS_EM_ANDAMENTO
                    if not carga.inicio_separacao:
                        carga.inicio_separacao = timezone.now()
                    carga.save()
                    controle.save()

                    # Atualiza controle se ainda estiver pendente
                    if controle.status == controle.STATUS_AGUARDANDO:
                        controle.status = controle.STATUS_EM_ANDAMENTO
                        if not controle.inicio_separacao:
                            controle.inicio_separacao = timezone.now()
                        controle.save()

                # =================== CONCLUIR CARGA ===================
                elif acao == "concluir" and carga.status != carga.STATUS_CONCLUIDO:
                    carga.status = carga.STATUS_CONCLUIDO
                    controle.STATUS_AGUARDANDO = controle.STATUS_CONCLUIDO
                    carga.finalizada = True
                    carga.save()

                    # Se todas as cargas estiverem concluídas, finaliza o controle
                    cargas_pendentes = controle.cargas.filter(status__in=[SeparacaoCarga.STATUS_EM_ANDAMENTO,
                                    SeparacaoCarga.STATUS_EM_ANDAMENTO]
                    )
                    if not cargas_pendentes.exists():
                        controle.finalizar_separacao()

                else:
                    # Apenas salva alterações de campos (atualização sem iniciar/concluir)
                    carga.save()

        except Exception as e:
            messages.error(request, f"Erro ao atualizar carga: {e}")
            return redirect("expedicao:editar_carga", pk=lecom.pk)

        messages.success(request, f"{carga} atualizada com sucesso.")
        return redirect("expedicao:cenario_separacao")
