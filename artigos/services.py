from django.db import transaction

from .models import LikeArtigo


@transaction.atomic
def transferir_likes_da_sessao(session_key, utilizador):
    """Converte likes anónimos em likes da conta sem duplicar contagens."""

    likes_anonimos = list(
        LikeArtigo.objects.select_for_update().filter(
            utilizador__isnull=True,
            session_key=session_key,
        )
    )
    for like in likes_anonimos:
        LikeArtigo.objects.get_or_create(
            artigo=like.artigo,
            utilizador=utilizador,
            defaults={'session_key': ''},
        )
        like.delete()
