from django.db import models
from transport.models import Lecom, Carga


class ControleSeparacao(models.Model):
    lecom = models.OneToOneField(
        Lecom,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="controle_separacao"
    )

    STATUS_PENDENTE = "Pendente"
    STATUS_AGUARDANDO = "Aguardando"
    STATUS_EM_ANDAMENTO = "Em Andamento"
    STATUS_CONCLUIDO = "Concluido"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_AGUARDANDO, "Aguardando"),
        (STATUS_EM_ANDAMENTO, "Em Andamento"),
        (STATUS_CONCLUIDO, "Concluído"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )

    liberada = models.BooleanField(default=False)
    inicio_separacao = models.DateTimeField(blank=True, null=True)
    finalizado = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def liberar_separacao(self):
        self.liberada = True
        self.status = self.STATUS_AGUARDANDO
        self.save()

    def finalizar_separacao(self):
        self.finalizado = True
        self.status = self.STATUS_CONCLUIDO
        self.save()

    def __str__(self):
        return f"Separação Lecom {self.lecom.lecom}"


class SeparacaoCarga(models.Model):
    controle = models.ForeignKey(ControleSeparacao,on_delete=models.CASCADE, related_name="cargas"
    )

    carga = models.ForeignKey(
        Carga,
        on_delete=models.CASCADE,
        related_name="separacoes"
    )

    seq = models.PositiveIntegerField()

    STATUS_PENDENTE = "Pendente"
    STATUS_EM_ANDAMENTO = "Em Andamento"
    STATUS_CONCLUIDO = "Concluido"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_EM_ANDAMENTO, "Em Andamento"),
        (STATUS_CONCLUIDO, "Concluído"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )

    numero_transporte = models.CharField(max_length=10)
    entregas = models.CharField(max_length=2, default="1")
    mod = models.CharField(max_length=10, default="-")
    resumo = models.CharField(max_length=2, default="1")
    ot = models.CharField(max_length=10, blank=True, default="")
    box = models.CharField(max_length=3, blank=True, null=True, default="Não informado")
    seg = models.CharField(max_length=10, default="")

    conferente = models.CharField(max_length=50, blank=True, null=True)
    separadores = models.CharField(max_length=100, blank=True, null=True)

    atribuida = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)

    resumo_conf = models.BooleanField(default=False)
    resumo_motorista = models.BooleanField(default=False)
    etiquetas_cds = models.BooleanField(default=False)
    carga_gerada = models.BooleanField(default=False)
    inicio_separacao = models.DateTimeField(null=True,blank=True,) 

    class Meta:
        ordering = ["seq"]
        unique_together = ("controle", "seq")

    def iniciar(self):
        self.status = self.STATUS_EM_ANDAMENTO
        self.atribuida = True
        self.save()

    def concluir(self):
        self.status = self.STATUS_CONCLUIDO
        self.finalizada = True
        self.save()

    def __str__(self):
        return f"SEQ {self.seq} | Carga {self.numero_transporte}"
