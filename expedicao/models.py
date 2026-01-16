from django.db import models
from django.utils import timezone
from transport.models import Lecom, Carga


class ControleSeparacao(models.Model):
    # 🔑 Lecom é a chave primária
    lecom = models.OneToOneField(
        Lecom,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="controle_separacao",
        verbose_name="Lecom"
    )

    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aguardando", "Aguardando"),
        ("Andamento", "Em Andamento"),
        ("Concluido", "Concluído"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pendente"
    )

    # =========================
    # CONTROLE REAL DO PROCESSO
    # =========================
    liberada = models.BooleanField(
        default=False,
        help_text="Só aparece no cenário quando True"
    )

    inicio_separacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Início da Separação"
    )

    finalizado = models.BooleanField(default=False)
    
    # RESPONSÁVEIS
    outros_separadores = models.CharField(
        max_length=255,
        blank=True,
        default="Não informado"
    )

    conferente = models.CharField(
        max_length=100,
        blank=True,
        default="Não informado"
    )

    # DOCUMENTOS
    resumo_conf = models.BooleanField(default=False)
    resumo_motorista = models.BooleanField(default=False)
    etiquetas_cds = models.BooleanField(default=False)
    carga_gerada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Controle de Separação"
        verbose_name_plural = "Controles de Separação"
        ordering = ["-criado_em"]


    def liberar_separacao(self):
        self.liberada = True
        self.status = "Aguardando"
        self.save()


    def finalizar_separacao(self):
        self.finalizado = True
        self.status = "Concluido"
        self.save()

    def __str__(self):
        return f"Separação Lecom {self.lecom.lecom}"



class SeparacaoCarga(models.Model):
    controle = models.ForeignKey(
        ControleSeparacao,
        on_delete=models.CASCADE,
        related_name="cargas"
    )

    carga = models.ForeignKey(
        Carga,
        on_delete=models.CASCADE,
        related_name="separacoes"
    )

    seq = models.PositiveIntegerField(
        verbose_name="SEQ da Carga"
    )

    numero_transporte = models.CharField(
        "Número da Carga",
        max_length=10
    )

    entregas = models.CharField(max_length=2, default="1")
    mod = models.CharField(max_length=10, default="-")

    resumo = models.CharField(max_length=2, default="1")

    ot = models.CharField(
        "Ordem de Transporte",
        max_length=10,
        blank=True,
        default=""
    )

    entrega_box = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        default="Não informado"
    )

    seg = models.CharField(
        max_length=10,
        default=""
    )

    atribuida = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Carga em Separação"
        verbose_name_plural = "Cargas em Separação"
        ordering = ["seq"]
        unique_together = ("controle", "seq")

    def __str__(self):
        return (
            f"SEQ {self.seq} | "
            f"Carga {self.numero_transporte} | "
            f"Lecom {self.carga.lecom.lecom}"
        )
