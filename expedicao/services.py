from expedicao.models import ControleSeparacao, SeparacaoCarga


def sincronizar_expedicao(lecom):
    """
    Sincroniza o cenário de expedição com o transporte (Lecom)
    """

    # 🔒 BLOQUEADO → remove da expedição
    if lecom.status == "BLOQUEADO":
        ControleSeparacao.objects.filter(lecom=lecom).delete()
        return

    # 🔓 LIBERADO → cria/atualiza
    controle, _ = ControleSeparacao.objects.get_or_create(
        lecom=lecom,
        defaults={"status": "Pendente"}
    )

    cargas_validas = []

    for carga in lecom.cargas.all():
        obj, _ = SeparacaoCarga.objects.update_or_create(
            controle=controle,
            carga=carga,
            defaults={
                "numero_transporte": carga.carga,
                "seq": carga.seq,
                "entregas": carga.total_entregas,
                "mod": carga.mod,
            }
        )
        cargas_validas.append(carga.id)

    # 🧹 Remove cargas que não existem mais
    SeparacaoCarga.objects.filter(
        controle=controle
    ).exclude(carga_id__in=cargas_validas).delete()

