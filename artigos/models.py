from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Artigo(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artigos')
    texto = models.TextField()
    fotografia = models.ImageField(upload_to='artigos/', blank=True)
    link_externo = models.URLField(blank=True)
    criado_em = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.autor.username} — {self.criado_em}'


class LikeArtigo(models.Model):
    artigo = models.ForeignKey(
        Artigo,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    utilizador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes_artigos',
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=64, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(utilizador__isnull=False) & Q(session_key=''))
                    | (Q(utilizador__isnull=True) & ~Q(session_key=''))
                ),
                name='like_tem_utilizador_ou_sessao',
            ),
            models.UniqueConstraint(
                fields=['artigo', 'utilizador'],
                condition=Q(utilizador__isnull=False),
                name='like_unico_por_utilizador',
            ),
            models.UniqueConstraint(
                fields=['artigo', 'session_key'],
                condition=~Q(session_key=''),
                name='like_unico_por_sessao',
            ),
        ]

    def __str__(self):
        identidade = self.utilizador or self.session_key
        return f'{identidade} gosta de artigo {self.artigo_id}'


class Comentario(models.Model):
    artigo = models.ForeignKey(Artigo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.autor.username}: {self.texto[:50]}'
