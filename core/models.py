from django.db import models

class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    senha = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.IntegerField()
    def __str__(self):
        return self.nome