from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    TIPO_CATEGORIA = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    )
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CATEGORIA)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class RegistroFinanceiro(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.CharField(max_length=255, blank=True, null=True)
    # O campo 'tipo' foi removido para evitar redundância.
    # A informação de tipo virá da Categoria associada.
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Podemos criar uma property para acessar o tipo facilmente
    @property
    def tipo(self):
        return self.categoria.tipo

    def __str__(self):
        return f"{self.data} — {self.categoria.get_tipo_display()}: {self.valor} ({self.categoria.nome})"
