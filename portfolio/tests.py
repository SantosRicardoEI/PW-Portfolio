from datetime import date

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
    Competencia,
    Docente,
    EvidenciaMakingOf,
    Formacao,
    Licenciatura,
    MakingOf,
    Projeto,
    Tecnologia,
    TFC,
    UnidadeCurricular,
)


class PortfolioModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.licenciatura = Licenciatura.objects.create(
            nome="Licenciatura em Engenharia Informática",
            sigla="LEI",
            codigo="260",
            descricao="Curso usado apenas pela base temporária de testes.",
            duracao_semestres=6,
            ects=180,
            website="https://www.ulusofona.pt/",
        )
        cls.docente = Docente.objects.create(
            nome="Docente de Teste",
            pagina_pessoal="https://www.ulusofona.pt/",
        )
        cls.uc = UnidadeCurricular.objects.create(
            licenciatura=cls.licenciatura,
            nome="Programação Web",
            codigo="PW",
            ano=2,
            semestre=2,
            ects=6,
            descricao="UC temporária para os testes.",
            imagem="unidades_curriculares/teste.jpg",
        )
        cls.uc.docentes.add(cls.docente)
        cls.tecnologia = Tecnologia.objects.create(
            nome="Django",
            categoria=Tecnologia.Categoria.FRAMEWORK,
            descricao="Framework web.",
            logo="tecnologias/django.png",
            website="https://www.djangoproject.com/",
            interesse=5,
            nivel=Tecnologia.Nivel.INTERMEDIO,
        )
        cls.projeto = Projeto.objects.create(
            titulo="Portfólio",
            descricao="Projeto temporário para os testes.",
            conceitos_aplicados="Modelação e ORM.",
            data=date(2026, 6, 24),
            imagem="projetos/portfolio.png",
            github_url="https://github.com/example/portfolio",
        )
        cls.projeto.unidades_curriculares.add(cls.uc)
        cls.projeto.tecnologias.add(cls.tecnologia)

    def test_relacoes_academicas_e_de_projeto(self):
        self.assertIn(self.docente, self.uc.docentes.all())
        self.assertIn(self.uc, self.projeto.unidades_curriculares.all())
        self.assertIn(self.tecnologia, self.projeto.tecnologias.all())
        self.assertEqual(str(self.licenciatura), "LEI — Licenciatura em Engenharia Informática")

    def test_interesse_da_tecnologia_esta_limitado_a_cinco(self):
        tecnologia = Tecnologia(
            nome="Inválida",
            categoria=Tecnologia.Categoria.OUTRA,
            descricao="Teste de validação.",
            logo="tecnologias/invalida.png",
            website="https://example.com/",
            interesse=6,
            nivel=Tecnologia.Nivel.INICIANTE,
        )
        with self.assertRaises(ValidationError):
            tecnologia.full_clean()

    def test_formacao_rejeita_data_final_anterior(self):
        formacao = Formacao(
            titulo="Formação inválida",
            instituicao="Instituição",
            tipo=Formacao.Tipo.CURSO,
            data_inicio=date(2026, 6, 24),
            data_fim=date(2026, 6, 23),
            descricao="Teste de validação.",
        )
        with self.assertRaises(ValidationError):
            formacao.full_clean()

    def test_competencias_e_formacoes_ficam_relacionadas(self):
        competencia = Competencia.objects.create(
            nome="Desenvolvimento web",
            categoria=Competencia.Categoria.TECNICA,
            descricao="Competência temporária para os testes.",
            nivel=Competencia.Nivel.INTERMEDIO,
        )
        competencia.projetos.add(self.projeto)
        competencia.tecnologias.add(self.tecnologia)
        formacao = Formacao.objects.create(
            titulo="Curso de Django",
            instituicao="Instituição",
            tipo=Formacao.Tipo.CURSO,
            data_inicio=date(2026, 1, 1),
            data_fim=date(2026, 2, 1),
            descricao="Formação temporária para os testes.",
        )
        formacao.competencias.add(competencia)

        self.assertIn(competencia, formacao.competencias.all())
        self.assertIn(self.projeto, competencia.projetos.all())

    def test_tfc_pode_ter_varios_orientadores(self):
        tfc = TFC.objects.create(
            titulo="TFC de teste",
            resumo="Registo existente apenas durante os testes.",
            ano=2025,
            estudante="Estudante de Teste",
            area="Web",
            interesse=4,
        )
        tfc.orientadores.add(self.docente)
        self.assertIn(self.docente, tfc.orientadores.all())

    def test_pastas_de_upload_estao_separadas(self):
        campo_uc = UnidadeCurricular._meta.get_field("imagem")
        campo_logo = Tecnologia._meta.get_field("logo")
        self.assertEqual(
            campo_uc.generate_filename(self.uc, "uc.jpg"),
            "unidades_curriculares/uc.jpg",
        )
        self.assertEqual(
            campo_logo.generate_filename(self.tecnologia, "logo.png"),
            "tecnologias/logo.png",
        )


class MakingOfTests(TestCase):
    def setUp(self):
        self.licenciatura = Licenciatura.objects.create(
            nome="Licenciatura em Engenharia Informática",
            sigla="LEI",
            codigo="260",
            descricao="Curso temporário para os testes.",
            duracao_semestres=6,
            ects=180,
        )
        self.content_type = ContentType.objects.get_for_model(self.licenciatura)

    def test_entrada_pode_documentar_qualquer_modelo_do_portfolio(self):
        entrada = MakingOf.objects.create(
            titulo="Modelação da licenciatura",
            fase=MakingOf.Fase.MODELO,
            descricao="Descrição do processo.",
            decisoes="Decisões justificadas.",
            content_type=self.content_type,
            object_id=self.licenciatura.pk,
        )
        EvidenciaMakingOf.objects.create(
            entrada=entrada,
            imagem="makingof/der.jpg",
            legenda="Fotografia real do DER.",
            ordem=1,
        )

        self.assertEqual(entrada.entidade_documentada, self.licenciatura)
        self.assertEqual(entrada.evidencias.count(), 1)

    def test_tipo_e_id_da_entidade_sao_preenchidos_em_conjunto(self):
        entrada = MakingOf(
            titulo="Entrada inválida",
            fase=MakingOf.Fase.MODELO,
            descricao="Descrição.",
            decisoes="Decisões.",
            content_type=self.content_type,
        )
        with self.assertRaises(ValidationError):
            entrada.full_clean()

    def test_id_da_entidade_tem_de_existir(self):
        entrada = MakingOf(
            titulo="Entrada inválida",
            fase=MakingOf.Fase.MODELO,
            descricao="Descrição.",
            decisoes="Decisões.",
            content_type=self.content_type,
            object_id=999999,
        )
        with self.assertRaises(ValidationError):
            entrada.full_clean()


class AdminOnlyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="teste-admin",
            email="",
            password="password-de-teste",
        )

    def test_todos_os_modelos_estao_registados_no_admin(self):
        modelos = {
            Licenciatura,
            Docente,
            UnidadeCurricular,
            Projeto,
            Tecnologia,
            TFC,
            Competencia,
            Formacao,
            MakingOf,
            EvidenciaMakingOf,
        }
        self.assertTrue(modelos.issubset(admin.site._registry.keys()))

    def test_admin_exige_login_e_fica_disponivel_apos_autenticacao(self):
        resposta = self.client.get(reverse("admin:index"))
        self.assertEqual(resposta.status_code, 302)

        self.client.force_login(self.user)
        resposta = self.client.get(reverse("admin:index"))
        self.assertEqual(resposta.status_code, 200)

    def test_nao_existe_pagina_publica(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 404)
