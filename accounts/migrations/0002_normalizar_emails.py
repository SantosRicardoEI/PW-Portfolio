from django.contrib.auth.hashers import is_password_usable
from django.db import migrations


def normalizar_emails(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Artigo = apps.get_model('artigos', 'Artigo')
    Comentario = apps.get_model('artigos', 'Comentario')
    LikeArtigo = apps.get_model('artigos', 'LikeArtigo')

    emails = {}
    for user in User.objects.exclude(email='').order_by('id'):
        normalized = user.email.strip().lower()
        emails.setdefault(normalized, []).append(user)

    for email, users in emails.items():
        canonical = sorted(
            users,
            key=lambda user: (
                not user.is_superuser,
                not user.is_staff,
                not is_password_usable(user.password),
                user.id,
            ),
        )[0]
        canonical.email = email

        for duplicate in users:
            if duplicate.pk == canonical.pk:
                continue

            Artigo.objects.filter(autor_id=duplicate.id).update(autor_id=canonical.id)
            Comentario.objects.filter(autor_id=duplicate.id).update(autor_id=canonical.id)
            for like in LikeArtigo.objects.filter(utilizador_id=duplicate.id):
                LikeArtigo.objects.get_or_create(
                    artigo_id=like.artigo_id,
                    utilizador_id=canonical.id,
                    defaults={'session_key': ''},
                )
                like.delete()

            canonical.groups.add(*duplicate.groups.all())
            canonical.user_permissions.add(*duplicate.user_permissions.all())
            if not is_password_usable(canonical.password) and is_password_usable(duplicate.password):
                canonical.password = duplicate.password
            for field in ('first_name', 'last_name'):
                if not getattr(canonical, field) and getattr(duplicate, field):
                    setattr(canonical, field, getattr(duplicate, field))
            duplicate.delete()

        canonical.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('artigos', '0002_likeartigo'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(normalizar_emails, migrations.RunPython.noop),
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX auth_user_email_ci_unique "
                "ON auth_user(LOWER(email)) WHERE email <> ''"
            ),
            reverse_sql='DROP INDEX IF EXISTS auth_user_email_ci_unique',
        ),
    ]
