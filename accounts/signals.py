from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .permissions import sync_group_permissions


@receiver(post_migrate)
def configure_groups(sender, app_config, **kwargs):
    if app_config.name in {"portfolio", "artigos"}:
        sync_group_permissions(app_config=app_config)
