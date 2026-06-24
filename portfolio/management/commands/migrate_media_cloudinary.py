from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from artigos.models import Artigo
from escola.models import Curso
from portfolio.models import (
    Docente,
    EvidenciaMakingOf,
    Formacao,
    Licenciatura,
    Projeto,
    Tecnologia,
    UnidadeCurricular,
)


MEDIA_FIELDS = (
    (Curso, 'imagem'),
    (Licenciatura, 'imagem'),
    (Docente, 'fotografia'),
    (UnidadeCurricular, 'imagem'),
    (Tecnologia, 'logo'),
    (Projeto, 'imagem'),
    (Formacao, 'certificado'),
    (EvidenciaMakingOf, 'imagem'),
    (Artigo, 'fotografia'),
)


class Command(BaseCommand):
    help = 'Migra ficheiros locais associados aos modelos para o Cloudinary.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Lista os ficheiros sem contactar nem alterar o Cloudinary.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if not dry_run and not settings.USE_CLOUDINARY:
            raise CommandError(
                'Cloudinary não está ativo. Configure CLOUDINARY_CLOUD_NAME, '
                'CLOUDINARY_API_KEY e CLOUDINARY_API_SECRET no .env.'
            )

        totals = {'candidates': 0, 'uploaded': 0, 'remote': 0, 'missing': 0}
        local_root = Path(settings.LOCAL_MEDIA_ROOT)

        for model, field_name in MEDIA_FIELDS:
            queryset = model.objects.exclude(**{field_name: ''})
            for instance in queryset.iterator():
                field_file = getattr(instance, field_name)
                if not field_file or not field_file.name:
                    continue

                totals['candidates'] += 1
                current_name = field_file.name
                local_path = local_root / current_name
                label = f'{model._meta.label} #{instance.pk}: {current_name}'

                if dry_run:
                    state = 'local' if local_path.is_file() else 'local em falta'
                    self.stdout.write(f'[DRY-RUN] {label} ({state})')
                    if not local_path.is_file():
                        totals['missing'] += 1
                    continue

                try:
                    if field_file.storage.exists(current_name):
                        totals['remote'] += 1
                        self.stdout.write(f'Já existe no Cloudinary: {label}')
                        continue
                except Exception as error:
                    raise CommandError(
                        f'Não foi possível consultar o Cloudinary para {label}: {error}'
                    ) from error

                if not local_path.is_file():
                    totals['missing'] += 1
                    self.stderr.write(self.style.WARNING(f'Ficheiro em falta: {label}'))
                    continue

                try:
                    with local_path.open('rb') as source:
                        field_file.save(local_path.name, File(source), save=True)
                except Exception as error:
                    raise CommandError(f'Falhou o upload de {label}: {error}') from error

                totals['uploaded'] += 1
                self.stdout.write(self.style.SUCCESS(f'Migrado: {label}'))

        self.stdout.write(
            self.style.SUCCESS(
                'Resumo: '
                f"{totals['candidates']} candidato(s), "
                f"{totals['uploaded']} migrado(s), "
                f"{totals['remote']} já remoto(s), "
                f"{totals['missing']} localmente em falta."
            )
        )
