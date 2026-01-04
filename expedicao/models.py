from django.db import models
from transport.models import Lecom, Carga


class ControleSeparacao(models.Model):
    lecom = models.ForeignKey(
        Lecom,
        on_delete=models.CASCADE,
        related_name="controles",
        verbose_name="Lecom"
    )

    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Andamento", "Em Andamento"),
        ("Concluido", "Concluído"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pendente"
    )

    inicio_separacao = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Início da Separação"
    )

    atribuida = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)

    # Separadores
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

    # Documentos
    resumo_conf = models.BooleanField(default=False)
    resumo_motorista = models.BooleanField(default=False)
    etiquetas_cds = models.BooleanField(default=False)
    carga_gerada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Controle de Separação"
        verbose_name_plural = "Controles de Separação"
        ordering = ["-criado_em"]
        unique_together = ("lecom",)  # 1 controle por lecom

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
        unique_together = ("controle", "seq")  # protege SEQ duplicado

    def __str__(self):
        return f"SEQ {self.seq} | Carga {self.numero_transporte} | Lecom {self.carga.lecom.lecom}"
