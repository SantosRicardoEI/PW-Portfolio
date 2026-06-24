from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.permissions import sync_group_permissions
from artigos.models import Artigo, Comentario, LikeArtigo
from portfolio.models import MakingOf


class Command(BaseCommand):
    help = 'Cria dados demonstrativos idempotentes para a Ficha 9.'

    @transaction.atomic
    def handle(self, *args, **options):
        sync_group_permissions()
        autores = Group.objects.get(name='autores')
        gestores = Group.objects.get(name='gestor-portfolio')

        autor, autor_criado = User.objects.get_or_create(
            username='autor_demo',
            defaults={'email': 'autor.demo@example.com'},
        )
        if autor_criado:
            autor.set_unusable_password()
            autor.save(update_fields=['password'])
        autor.groups.add(autores)

        gestor, gestor_criado = User.objects.get_or_create(
            username='gestor',
            defaults={
                'email': 'gestor@example.com',
                'is_staff': True,
            },
        )
        if gestor_criado:
            gestor.set_unusable_password()
        if not gestor.is_staff:
            gestor.is_staff = True
        gestor.save()
        gestor.groups.add(gestores)

        marcador = '[DEMO FICHA 9]'
        artigo = Artigo.objects.filter(
            autor=autor,
            texto__startswith=marcador,
        ).first()
        if artigo is None:
            artigo = Artigo.objects.create(
                autor=autor,
                texto=(
                    f'{marcador} Autenticação e autorização em Django permitem '
                    'separar identidade, grupos e permissões. Nesta aplicação, '
                    'gestores administram o portfólio e autores publicam apenas '
                    'os seus próprios artigos.'
                ),
                link_externo='https://docs.djangoproject.com/en/5.2/topics/auth/',
            )

        if not artigo.fotografia:
            source_path = Path(settings.MEDIA_ROOT) / 'cursos' / 'django.png'
            if source_path.exists():
                with source_path.open('rb') as source:
                    artigo.fotografia.save(
                        'django-ficha9.png',
                        File(source),
                        save=True,
                    )

        Comentario.objects.get_or_create(
            artigo=artigo,
            autor=gestor,
            texto='Exemplo de comentário autenticado para demonstrar a Ficha 9.',
        )
        LikeArtigo.objects.get_or_create(
            artigo=artigo,
            utilizador=gestor,
            defaults={'session_key': ''},
        )
        LikeArtigo.objects.get_or_create(
            artigo=artigo,
            utilizador=None,
            session_key='demo-ficha9-anonimo',
        )

        MakingOf.objects.get_or_create(
            titulo='Autenticação, autorização e artigos — Ficha 9',
            defaults={
                'fase': MakingOf.Fase.IMPLEMENTACAO,
                'descricao': (
                    'Foram implementados login por password e link mágico, '
                    'autorização por grupos, artigos com propriedade, likes '
                    'anónimos por sessão e comentários autenticados.'
                ),
                'decisoes': (
                    'Os controlos de grupo são aplicados nas views e não apenas '
                    'nos templates. Likes anónimos usam a sessão, evitando '
                    'recolher endereços IP.'
                ),
                'erros': (
                    'A versão inicial permitia que qualquer utilizador autenticado '
                    'acedesse diretamente ao CRUD do portfólio e alterava likes '
                    'através de pedidos GET.'
                ),
                'correcoes': (
                    'Foram adicionados decoradores de grupo, respostas 403, '
                    'endpoints POST e constraints de unicidade na base de dados.'
                ),
                'uso_ia': (
                    'O Codex foi usado para auditar o enunciado, identificar '
                    'falhas de autorização, apoiar a implementação e criar testes. '
                    'As decisões e o resultado foram revistos no projeto.'
                ),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Dados demo prontos: artigo {artigo.id}, '
                f'{artigo.likes.count()} likes e '
                f'{artigo.comentarios.count()} comentário(s).'
            )
        )
