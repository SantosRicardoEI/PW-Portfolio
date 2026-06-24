from django.db import models
from django.contrib.auth.models import User


class Artigo(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artigos')
    texto = models.TextField()
    fotografia = models.ImageField(upload_to='artigos/', blank=True)
    link_externo = models.URLField(blank=True)
    criado_em = models.DateField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='artigos_liked', blank=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.autor.username} — {self.criado_em}'


class Comentario(models.Model):
    artigo = models.ForeignKey(Artigo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.autor.username}: {self.texto[:50]}'
