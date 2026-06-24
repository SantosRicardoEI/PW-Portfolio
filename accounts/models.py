import secrets
from django.db import models
from django.utils import timezone


class MagicLinkToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def is_valido(self):
        # token válido por 15 minutos e não usado
        expira = self.criado_em + timezone.timedelta(minutes=15)
        return not self.usado and timezone.now() < expira

    @classmethod
    def criar(cls, email):
        return cls.objects.create(email=email, token=secrets.token_urlsafe(32))
