from datetime import date
from django.db.models import Sum
from transport.models import Lecom
from receipt.models import NotaFiscal

def get_context_recebimento():
    hoje = date.today()
    # Total de notas do dia
    notas = NotaFiscal.objects.filter(data=hoje).count()
    
    # Contagem por quantidade de paletes (ajuste conforme seu campo)
    un10 = NotaFiscal.objects.filter(data=hoje, qnt_pallet="10").count()
    un20 = NotaFiscal.objects.filter(data=hoje, qnt_pallet="20").count()
    un40 = NotaFiscal.objects.filter(data=hoje, qnt_pallet="40").count()

    # Soma do peso das notas do dia
    total_peso = NotaFiscal.objects.filter(data=hoje).aggregate(Sum("peso_nota"))["peso_nota__sum"] or 0

    return {
        "notas": notas,
        "un10": un10,
        "un20": un20,
        "un40": un40,
        "total": notas,
        "total_peso": total_peso,
    }


def get_context_transporte():
    hoje = date.today()
    lecom_hoje = Lecom.objects.filter(data=hoje)
    
    total_lecoms = lecom_hoje.count()
    total_peso = lecom_hoje.aggregate(Sum("peso"))["peso__sum"] or 0

    # Aqui você pode adicionar outros cálculos específicos do transporte se quiser
    return {
        "total_lecoms": total_lecoms,
        "total_peso_transp": total_peso,
        # Exemplo fictício de unidades
        "un20_transp": 4,
        "un40_transp": 2,
        "total_transp": total_lecoms,
    }
