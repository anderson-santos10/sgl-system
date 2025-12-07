from django.db import models

class ControleSeparacao(models.Model):
    lecom = models.CharField(max_length=10, default="")
    numero_transporte = models.CharField("Número da Carga", max_length=10) 
    resumo = models.CharField(max_length=2, default="1")
    destino = models.CharField(max_length=150, default="")
    uf = models.CharField(max_length=2, default="")
    peso = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    entregas = models.CharField(max_length=2, default="1")
    mod = models.CharField(max_length=10, default="")
    data = models.DateField(verbose_name="Data da Carga", auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True, default="")
    ot = models.CharField("Ordem de Transporte", max_length=10)
    entrega_box = models.CharField(max_length=3, blank=True, null=True, default="Não informado")
    seg = models.CharField(max_length=10, default="")
    m3 = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    # Tipo de Veículo
    TIPO_VEICULO_CHOICES = [
        ("3/4", "3/4"),
        ("toco", "Toco"),
        ("carreta", "Carreta"),
        ("truck", "Truck"),
        ("rodotrem", "Rodotrem"),
        ("container", "Container"),
        ("utilitario", "Utilitário"),
    ]
    tipo_veiculo = models.CharField(max_length=20, choices=TIPO_VEICULO_CHOICES, blank=True, default="Não informado")

    # Separadores e Conferente
    outros_separadores = models.CharField(max_length=255, blank=True, default="Não informado")
    conferente = models.CharField(max_length=100, blank=True, default="Não informado")

    # Início separação
    inicio_separacao = models.TimeField(blank=True, null=True)

    # Documentos
    resumo_conf = models.BooleanField(default=False)
    resumo_motorista = models.BooleanField(default=False)
    etiquetas_cds = models.BooleanField(default=False)
    carga_gerada = models.BooleanField(default=False)

    # Status da carga
    atribuida = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Andamento", "Em Andamento"),
        ("Concluido", "Concluído"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pendente")

    def __str__(self):
        return f"Carga {self.id} - {self.numero_transporte}"
