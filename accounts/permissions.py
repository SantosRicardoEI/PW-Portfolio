from django.contrib.auth.models import Group, Permission


def sync_group_permissions(app_config=None, **kwargs):
    """Mantém os grupos da Ficha 9 coerentes após cada migrate."""

    app_name = getattr(app_config, "name", None)

    if app_name in (None, "portfolio"):
        gestor, _ = Group.objects.get_or_create(name="gestor-portfolio")
        portfolio_permissions = Permission.objects.filter(
            content_type__app_label="portfolio"
        )
        gestor.permissions.set(portfolio_permissions)

    if app_name in (None, "artigos"):
        autores, _ = Group.objects.get_or_create(name="autores")
        artigo_permissions = Permission.objects.filter(
            content_type__app_label="artigos",
            content_type__model__in=("artigo", "comentario"),
        )
        autores.permissions.set(artigo_permissions)
