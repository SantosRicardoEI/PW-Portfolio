from tempfile import TemporaryDirectory

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.permissions import sync_group_permissions
from artigos.models import Artigo, Comentario, LikeArtigo


class ArtigosTests(TestCase):
    def setUp(self):
        sync_group_permissions()
        autores = Group.objects.get(name='autores')
        self.autor = User.objects.create_user(
            'autor', email='autor@example.com', password='Password-123'
        )
        self.autor.groups.add(autores)
        self.outro_autor = User.objects.create_user(
            'outro', email='outro@example.com', password='Password-123'
        )
        self.outro_autor.groups.add(autores)
        self.comum = User.objects.create_user(
            'comum', email='comum@example.com', password='Password-123'
        )
        self.superuser = User.objects.create_superuser(
            'super-artigos', email='super@exemplo.com', password='Password-123'
        )
        self.artigo = Artigo.objects.create(
            autor=self.autor,
            texto='Artigo de teste',
            link_externo='https://example.com/artigo',
        )

    def test_lista_e_publica_e_botao_criar_so_aparece_a_autores(self):
        response = self.client.get(reverse('artigos_lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artigo.texto)
        self.assertNotContains(response, 'Novo artigo')

        self.client.force_login(self.comum)
        self.assertNotContains(self.client.get(reverse('artigos_lista')), 'Novo artigo')
        self.client.logout()

        self.client.force_login(self.autor)
        self.assertContains(self.client.get(reverse('artigos_lista')), 'Novo artigo')

        self.autor.groups.clear()
        response = self.client.get(reverse('artigos_lista'))
        self.assertNotContains(response, 'Novo artigo')
        self.assertNotContains(response, '>Editar<')

    def test_so_autores_criam_e_so_proprietario_edita_ou_apaga(self):
        self.assertEqual(self.client.get(reverse('artigo_criar')).status_code, 302)

        self.client.force_login(self.comum)
        self.assertEqual(self.client.get(reverse('artigo_criar')).status_code, 403)
        self.client.logout()

        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(reverse('artigo_criar')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('artigo_editar', args=[self.artigo.id])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('artigo_apagar', args=[self.artigo.id])).status_code,
            200,
        )
        self.client.logout()

        self.client.force_login(self.outro_autor)
        self.assertEqual(
            self.client.get(reverse('artigo_editar', args=[self.artigo.id])).status_code,
            404,
        )
        self.client.logout()

        self.client.force_login(self.superuser)
        self.assertEqual(
            self.client.get(reverse('artigo_editar', args=[self.artigo.id])).status_code,
            200,
        )

    def test_like_anonimo_alterna_apenas_por_post(self):
        url = reverse('artigo_like', args=[self.artigo.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        like = LikeArtigo.objects.get(artigo=self.artigo)
        self.assertIsNone(like.utilizador)
        self.assertEqual(like.session_key, self.client.session.session_key)

        self.client.post(url)
        self.assertFalse(LikeArtigo.objects.filter(artigo=self.artigo).exists())

    def test_sessoes_anonimas_contam_como_pessoas_distintas(self):
        url = reverse('artigo_like', args=[self.artigo.id])
        outro_browser = Client()
        self.client.post(url)
        outro_browser.post(url)
        self.assertEqual(LikeArtigo.objects.filter(artigo=self.artigo).count(), 2)

    def test_like_autenticado_e_transferencia_do_like_anonimo(self):
        url = reverse('artigo_like', args=[self.artigo.id])
        self.client.post(url)
        session_key = self.client.session.session_key

        response = self.client.post(
            reverse('login'),
            {
                'username': self.autor.username,
                'password': 'Password-123',
                'next': reverse('artigos_lista'),
            },
        )
        self.assertRedirects(response, reverse('artigos_lista'))
        self.assertFalse(
            LikeArtigo.objects.filter(
                artigo=self.artigo, session_key=session_key
            ).exists()
        )
        self.assertTrue(
            LikeArtigo.objects.filter(
                artigo=self.artigo, utilizador=self.autor
            ).exists()
        )
        self.assertEqual(LikeArtigo.objects.filter(artigo=self.artigo).count(), 1)

    def test_constraints_impedem_likes_sem_identidade_e_duplicados(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            LikeArtigo.objects.create(artigo=self.artigo)

        LikeArtigo.objects.create(artigo=self.artigo, utilizador=self.autor)
        with self.assertRaises(IntegrityError), transaction.atomic():
            LikeArtigo.objects.create(artigo=self.artigo, utilizador=self.autor)

    def test_comentarios_exigem_autenticacao(self):
        url = reverse('comentario_criar', args=[self.artigo.id])
        response = self.client.post(url, {'texto': 'Comentário'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comentario.objects.exists())

        self.client.force_login(self.comum)
        self.client.post(url, {'texto': 'Comentário autenticado'})
        comentario = Comentario.objects.get()
        self.assertEqual(comentario.autor, self.comum)
        self.assertEqual(comentario.artigo, self.artigo)

    def test_seed_demo_e_idempotente(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                call_command('seed_ficha9_demo', verbosity=0)
                call_command('seed_ficha9_demo', verbosity=0)

        artigo = Artigo.objects.get(texto__startswith='[DEMO FICHA 9]')
        self.assertEqual(artigo.comentarios.count(), 1)
        self.assertEqual(artigo.likes.count(), 2)
        self.assertEqual(
            Artigo.objects.filter(texto__startswith='[DEMO FICHA 9]').count(),
            1,
        )
