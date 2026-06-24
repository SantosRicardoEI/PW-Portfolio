from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts.permissions import sync_group_permissions
from portfolio.models import (
    Competencia,
    Formacao,
    Licenciatura,
    Projeto,
    Tecnologia,
    UnidadeCurricular,
)


class PortfolioPermissionsTests(TestCase):
    def setUp(self):
        sync_group_permissions()
        self.normal = User.objects.create_user('normal', password='Password-123')
        self.gestor = User.objects.create_user('gestor-test', password='Password-123')
        self.gestor.groups.add(Group.objects.get(name='gestor-portfolio'))
        self.superuser = User.objects.create_superuser(
            'super-test', email='super@example.com', password='Password-123'
        )

        licenciatura = Licenciatura.objects.create(
            nome='Engenharia Informática', sigla='LEI-T', codigo='LEI-TEST'
        )
        uc = UnidadeCurricular.objects.create(
            licenciatura=licenciatura,
            nome='Programação Web',
            codigo='PW-TEST',
            ano=3,
            semestre=UnidadeCurricular.Semestre.SEGUNDO,
            ects=6,
        )
        tecnologia = Tecnologia.objects.create(nome='Tecnologia Teste')
        projeto = Projeto.objects.create(
            titulo='Projeto Teste',
            descricao='Descrição',
            conceitos_aplicados='MVT',
            data=date(2026, 1, 1),
            imagem='projetos/teste.png',
            github_url='https://github.com/example/teste',
        )
        projeto.unidades_curriculares.add(uc)
        competencia = Competencia.objects.create(
            nome='Competência Teste',
            categoria=Competencia.Categoria.TECNICA,
            descricao='Descrição',
            nivel=Competencia.Nivel.INTERMEDIO,
        )
        formacao = Formacao.objects.create(
            titulo='Formação Teste',
            instituicao='Instituição',
            tipo=Formacao.Tipo.CURSO,
            data_inicio=date(2025, 1, 1),
            descricao='Descrição',
        )

        self.paths = [
            reverse('projeto_criar'),
            reverse('projeto_editar', args=[projeto.id]),
            reverse('projeto_apagar', args=[projeto.id]),
            reverse('tecnologia_criar'),
            reverse('tecnologia_editar', args=[tecnologia.id]),
            reverse('tecnologia_apagar', args=[tecnologia.id]),
            reverse('competencia_criar'),
            reverse('competencia_editar', args=[competencia.id]),
            reverse('competencia_apagar', args=[competencia.id]),
            reverse('formacao_criar'),
            reverse('formacao_editar', args=[formacao.id]),
            reverse('formacao_apagar', args=[formacao.id]),
        ]

    def test_anonimo_e_redirecionado_em_todo_o_crud(self):
        for path in self.paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_utilizador_sem_grupo_recebe_403_em_todo_o_crud(self):
        self.client.force_login(self.normal)
        for path in self.paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)

    def test_gestor_e_superuser_acedem_a_todo_o_crud(self):
        for user in (self.gestor, self.superuser):
            self.client.force_login(user)
            for path in self.paths:
                with self.subTest(user=user.username, path=path):
                    self.assertEqual(self.client.get(path).status_code, 200)
            self.client.logout()

    def test_botoes_so_aparecem_ao_gestor_ou_superuser(self):
        for user, visible in (
            (self.normal, False),
            (self.gestor, True),
            (self.superuser, True),
        ):
            self.client.force_login(user)
            response = self.client.get(reverse('projetos'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual('Novo Projeto' in response.content.decode(), visible)
            self.client.logout()
