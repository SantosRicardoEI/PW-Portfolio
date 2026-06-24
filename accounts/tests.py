from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import MagicLinkToken
from .permissions import sync_group_permissions


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AccountsTests(TestCase):
    def setUp(self):
        sync_group_permissions()

    def test_login_valida_credenciais_e_respeita_next_seguro(self):
        user = User.objects.create_user('ricardo', password='Password-forte-123')
        response = self.client.post(
            reverse('login'),
            {
                'username': user.username,
                'password': 'Password-forte-123',
                'next': reverse('artigos_lista'),
            },
        )
        self.assertRedirects(response, reverse('artigos_lista'))
        self.assertEqual(str(user.id), self.client.session['_auth_user_id'])

        self.client.logout()
        response = self.client.post(
            reverse('login'),
            {
                'username': user.username,
                'password': 'Password-forte-123',
                'next': 'https://example.com/roubo',
            },
        )
        self.assertRedirects(response, reverse('projetos'))

    def test_login_invalido_apresenta_erro(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'inexistente', 'password': 'errada'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credenciais inválidas')

    def test_registo_exige_email_unico_e_adiciona_autores(self):
        response = self.client.post(
            reverse('registo'),
            {
                'username': 'novo-autor',
                'email': 'AUTOR@example.com',
                'password1': 'Password-forte-123',
                'password2': 'Password-forte-123',
            },
        )
        self.assertRedirects(response, reverse('artigos_lista'))
        user = User.objects.get(username='novo-autor')
        self.assertEqual(user.email, 'autor@example.com')
        self.assertTrue(user.groups.filter(name='autores').exists())

        self.client.logout()
        response = self.client.post(
            reverse('registo'),
            {
                'username': 'duplicado',
                'email': 'autor@EXAMPLE.com',
                'password1': 'Password-forte-123',
                'password2': 'Password-forte-123',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Já existe uma conta com este email')
        self.assertFalse(User.objects.filter(username='duplicado').exists())

    def test_logout_so_aceita_post(self):
        user = User.objects.create_user('utilizador', password='Password-forte-123')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_link_magico_reutiliza_conta_e_so_funciona_uma_vez(self):
        user = User.objects.create_user(
            'conta-existente',
            email='existente@example.com',
        )
        response = self.client.post(
            reverse('magic_link_pedido'),
            {'email': 'EXISTENTE@example.com'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        token = MagicLinkToken.objects.get()

        response = self.client.get(reverse('magic_link_verificar', args=[token.token]))
        self.assertRedirects(response, reverse('projetos'))
        user.refresh_from_db()
        self.assertTrue(user.groups.filter(name='autores').exists())
        self.assertEqual(User.objects.filter(email__iexact=user.email).count(), 1)

        self.client.logout()
        response = self.client.get(reverse('magic_link_verificar', args=[token.token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Link inválido ou expirado')

    def test_link_magico_cria_nova_conta_autora(self):
        token = MagicLinkToken.criar('nova@example.com')
        response = self.client.get(reverse('magic_link_verificar', args=[token.token]))
        self.assertRedirects(response, reverse('projetos'))
        user = User.objects.get(email='nova@example.com')
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.groups.filter(name='autores').exists())

    def test_link_magico_rejeita_email_invalido(self):
        response = self.client.post(
            reverse('magic_link_pedido'),
            {'email': 'email-invalido'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Introduza um endereço de e-mail válido')
        self.assertFalse(MagicLinkToken.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_link_magico_expira_e_novo_pedido_invalida_anterior(self):
        expirado = MagicLinkToken.criar('expirado@example.com')
        MagicLinkToken.objects.filter(pk=expirado.pk).update(
            criado_em=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.get(
            reverse('magic_link_verificar', args=[expirado.token])
        )
        self.assertContains(response, 'Link inválido ou expirado')

        anterior = MagicLinkToken.criar('renovar@example.com')
        atual = MagicLinkToken.criar('RENOVAR@example.com')
        anterior.refresh_from_db()
        self.assertTrue(anterior.usado)
        self.assertFalse(atual.usado)

    def test_grupos_ficam_limitados_as_apps_corretas(self):
        gestor = Group.objects.get(name='gestor-portfolio')
        autores = Group.objects.get(name='autores')
        self.assertEqual(
            set(gestor.permissions.values_list('content_type__app_label', flat=True)),
            {'portfolio'},
        )
        self.assertEqual(
            set(autores.permissions.values_list('content_type__app_label', flat=True)),
            {'artigos'},
        )

    def test_email_e_unico_sem_distinguir_maiusculas(self):
        User.objects.create_user('primeiro', email='unico@example.com')
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user('segundo', email='UNICO@example.com')
