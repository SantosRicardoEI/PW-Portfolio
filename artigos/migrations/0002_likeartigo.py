import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrar_likes(apps, schema_editor):
    Artigo = apps.get_model('artigos', 'Artigo')
    LikeArtigo = apps.get_model('artigos', 'LikeArtigo')
    for artigo in Artigo.objects.prefetch_related('likes'):
        LikeArtigo.objects.bulk_create(
            [
                LikeArtigo(artigo_id=artigo.id, utilizador_id=user.id)
                for user in artigo.likes.all()
            ],
            ignore_conflicts=True,
        )


def repor_likes(apps, schema_editor):
    Artigo = apps.get_model('artigos', 'Artigo')
    LikeArtigo = apps.get_model('artigos', 'LikeArtigo')
    for artigo in Artigo.objects.all():
        user_ids = LikeArtigo.objects.filter(
            artigo_id=artigo.id,
            utilizador_id__isnull=False,
        ).values_list('utilizador_id', flat=True)
        artigo.likes.add(*user_ids)


class Migration(migrations.Migration):

    dependencies = [
        ('artigos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeArtigo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=64)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('artigo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='artigos.artigo')),
                ('utilizador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes_artigos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['criado_em'],
                'constraints': [
                    models.CheckConstraint(
                        condition=(
                            (models.Q(utilizador__isnull=False) & models.Q(session_key=''))
                            | (models.Q(utilizador__isnull=True) & ~models.Q(session_key=''))
                        ),
                        name='like_tem_utilizador_ou_sessao',
                    ),
                    models.UniqueConstraint(
                        fields=('artigo', 'utilizador'),
                        condition=models.Q(utilizador__isnull=False),
                        name='like_unico_por_utilizador',
                    ),
                    models.UniqueConstraint(
                        fields=('artigo', 'session_key'),
                        condition=~models.Q(session_key=''),
                        name='like_unico_por_sessao',
                    ),
                ],
            },
        ),
        migrations.RunPython(migrar_likes, repor_likes),
        migrations.RemoveField(
            model_name='artigo',
            name='likes',
        ),
    ]
