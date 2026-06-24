from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Licenciatura(models.Model):
    """Curso frequentado e respetiva informação institucional."""

    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=20)
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código usado pela instituição (por exemplo, 260 para LEI).",
    )
    descricao = models.TextField(blank=True)
    duracao_semestres = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
    )
    ects = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
    )
    website = models.URLField(blank=True)
    imagem = models.ImageField(upload_to="licenciaturas/", blank=True)
    objetivos = models.TextField(blank=True)
    competencias = models.TextField(blank=True)
    saidas_profissionais = models.TextField(blank=True)
    condicoes_acesso = models.TextField(blank=True)
    grau = models.CharField(max_length=100, blank=True)
    area_cientifica = models.CharField(max_length=150, blank=True)
    modalidade = models.CharField(max_length=100, blank=True)
    acreditacao = models.CharField(max_length=100, blank=True)
    docentes = models.ManyToManyField(
        "Docente",
        related_name="licenciaturas",
        blank=True,
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "licenciatura"
        verbose_name_plural = "licenciaturas"

    def __str__(self):
        return f"{self.sigla} — {self.nome}"


class Docente(models.Model):
    """Entidade adicional que evita repetir docentes em cada UC e TFC."""

    nome = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    pagina_pessoal = models.URLField(
        blank=True,
        help_text="Ligação para a página pessoal no site da Universidade Lusófona."
    )
    fotografia = models.ImageField(upload_to="docentes/", blank=True)
    ativo = models.BooleanField(default=True)
    nome_completo = models.CharField(max_length=200, blank=True)
    grau = models.CharField(max_length=100, blank=True)
    regime = models.CharField(max_length=100, blank=True)
    orcid = models.CharField(max_length=30, blank=True)
    ciencia_vitae = models.CharField(max_length=30, blank=True)
    codigo_funcionario = models.PositiveIntegerField(
        blank=True,
        null=True,
        unique=True,
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "docente"
        verbose_name_plural = "docentes"

    def __str__(self):
        return self.nome


class UnidadeCurricular(models.Model):
    """Unidade curricular pertencente a uma licenciatura."""

    class Semestre(models.TextChoices):
        PRIMEIRO = "S1", "1.º semestre"
        SEGUNDO = "S2", "2.º semestre"
        ANUAL = "A", "Anual"

    licenciatura = models.ForeignKey(
        Licenciatura,
        on_delete=models.CASCADE,
        related_name="unidades_curriculares",
    )
    docentes = models.ManyToManyField(
        Docente,
        related_name="unidades_curriculares",
        blank=True,
    )
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30)
    ano = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    semestre = models.CharField(max_length=2, choices=Semestre.choices)
    ects = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0.5)],
    )
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to="unidades_curriculares/", blank=True)
    ano_letivo = models.CharField(max_length=6, blank=True)
    apresentacao = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)
    competencias = models.TextField(blank=True)
    programa = models.TextField(blank=True)
    metodologia = models.TextField(blank=True)
    avaliacao = models.TextField(blank=True)
    bibliografia = models.TextField(blank=True)
    natureza = models.CharField(max_length=100, blank=True)
    idioma = models.CharField(max_length=100, blank=True)
    horas_contacto = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["licenciatura", "ano", "semestre", "nome"]
        verbose_name = "unidade curricular"
        verbose_name_plural = "unidades curriculares"
        constraints = [
            models.UniqueConstraint(
                fields=["licenciatura", "codigo"],
                name="uc_codigo_unico_por_licenciatura",
            )
        ]

    def __str__(self):
        return f"{self.codigo} — {self.nome}"


class TipoTecnologia(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "tipo de tecnologia"
        verbose_name_plural = "tipos de tecnologia"

    def __str__(self):
        return self.nome


class Tecnologia(models.Model):
    class Categoria(models.TextChoices):
        LINGUAGEM = "linguagem", "Linguagem de programação"
        FRAMEWORK = "framework", "Framework"
        BASE_DADOS = "base_dados", "Base de dados"
        FERRAMENTA = "ferramenta", "Ferramenta"
        PLATAFORMA = "plataforma", "Plataforma"
        OUTRA = "outra", "Outra"

    class Nivel(models.TextChoices):
        INICIANTE = "iniciante", "Iniciante"
        INTERMEDIO = "intermedio", "Intermédio"
        AVANCADO = "avancado", "Avançado"

    nome = models.CharField(max_length=100, unique=True)
    tipo = models.ForeignKey(
        TipoTecnologia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tecnologias',
    )
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        blank=True,
    )
    descricao = models.TextField(blank=True)
    logo = models.ImageField(upload_to="tecnologias/", blank=True)
    website = models.URLField(
        blank=True,
        help_text="Website oficial da tecnologia.",
    )
    interesse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text="Classificação pessoal entre 1 e 5.",
    )
    nivel = models.CharField(max_length=15, choices=Nivel.choices, blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "tecnologia"
        verbose_name_plural = "tecnologias"

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    conceitos_aplicados = models.TextField(
        help_text="Conceitos das unidades curriculares aplicados no projeto."
    )
    data = models.DateField()
    imagem = models.ImageField(upload_to="projetos/")
    github_url = models.URLField(verbose_name="repositório GitHub")
    demo_url = models.URLField(blank=True, verbose_name="demonstração")
    video_url = models.URLField(blank=True, verbose_name="vídeo")
    destaque = models.BooleanField(default=False)
    unidades_curriculares = models.ManyToManyField(
        UnidadeCurricular,
        related_name="projetos",
    )
    tecnologias = models.ManyToManyField(
        Tecnologia,
        related_name="projetos",
        blank=True,
    )

    class Meta:
        ordering = ["-data", "titulo"]
        verbose_name = "projeto"
        verbose_name_plural = "projetos"

    def __str__(self):
        return self.titulo


class Aluno(models.Model):
    nome = models.CharField(max_length=150, blank=True)
    numero = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="número académico",
    )

    class Meta:
        ordering = ["nome", "numero"]
        verbose_name = "aluno"
        verbose_name_plural = "alunos"

    def __str__(self):
        if self.nome and self.numero:
            return f"{self.nome} ({self.numero})"
        return self.nome or self.numero or "Aluno sem identificação"


class AreaTFC(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "área de TFC"
        verbose_name_plural = "áreas de TFC"

    def __str__(self):
        return self.nome


class PalavraChaveTFC(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "palavra-chave de TFC"
        verbose_name_plural = "palavras-chave de TFC"

    def __str__(self):
        return self.nome


class TFC(models.Model):
    class Estado(models.TextChoices):
        EM_CURSO = "em_curso", "Em curso"
        CONCLUIDO = "concluido", "Concluído"

    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.CONCLUIDO,
    )
    titulo = models.CharField(max_length=200)
    resumo = models.TextField()
    ano = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    email = models.EmailField(blank=True, default="")
    parceria = models.CharField(max_length=255, blank=True, default="")
    relatorio_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="relatório",
    )
    imagem_url = models.URLField(max_length=500, blank=True, verbose_name="imagem")
    video_url = models.URLField(max_length=500, blank=True, verbose_name="vídeo")
    alunos = models.ManyToManyField(Aluno, related_name="tfcs", blank=True)
    orientadores = models.ManyToManyField(
        Docente,
        related_name="tfcs_orientados",
        blank=True,
    )
    licenciaturas = models.ManyToManyField(
        Licenciatura,
        related_name="tfcs",
        blank=True,
    )
    areas = models.ManyToManyField(AreaTFC, related_name="tfcs", blank=True)
    palavras_chave = models.ManyToManyField(
        PalavraChaveTFC,
        related_name="tfcs",
        blank=True,
    )
    tecnologias = models.ManyToManyField(
        Tecnologia,
        related_name="tfcs",
        blank=True,
    )
    interesse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text="Classificação pessoal entre 1 e 5.",
    )
    destaque = models.BooleanField(default=False)

    class Meta:
        ordering = ["-ano", "titulo"]
        verbose_name = "TFC"
        verbose_name_plural = "TFCs"
        constraints = [
            models.UniqueConstraint(
                fields=["titulo", "ano", "email"],
                name="tfc_titulo_ano_email_unicos",
            )
        ]

    def __str__(self):
        return f"{self.titulo} ({self.ano})"


class Competencia(models.Model):
    class Categoria(models.TextChoices):
        TECNICA = "tecnica", "Técnica"
        INTERPESSOAL = "interpessoal", "Interpessoal"
        LINGUISTICA = "linguistica", "Linguística"
        OUTRA = "outra", "Outra"

    class Nivel(models.TextChoices):
        BASICO = "basico", "Básico"
        INTERMEDIO = "intermedio", "Intermédio"
        AVANCADO = "avancado", "Avançado"

    nome = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    descricao = models.TextField()
    nivel = models.CharField(max_length=15, choices=Nivel.choices)
    projetos = models.ManyToManyField(
        Projeto,
        related_name="competencias",
        blank=True,
    )
    tecnologias = models.ManyToManyField(
        Tecnologia,
        related_name="competencias",
        blank=True,
    )

    class Meta:
        ordering = ["categoria", "nome"]
        verbose_name = "competência"
        verbose_name_plural = "competências"

    def __str__(self):
        return self.nome


class Formacao(models.Model):
    class Tipo(models.TextChoices):
        ACADEMICA = "academica", "Académica"
        CURSO = "curso", "Curso"
        CERTIFICACAO = "certificacao", "Certificação"
        WORKSHOP = "workshop", "Workshop"
        OUTRA = "outra", "Outra"

    titulo = models.CharField(max_length=150)
    instituicao = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    em_curso = models.BooleanField(default=False)
    descricao = models.TextField()
    certificado = models.FileField(upload_to="formacoes/certificados/", blank=True)
    url = models.URLField(blank=True)
    competencias = models.ManyToManyField(
        Competencia,
        related_name="formacoes",
        blank=True,
    )

    class Meta:
        ordering = ["-data_inicio", "titulo"]
        verbose_name = "formação"
        verbose_name_plural = "formações"

    def __str__(self):
        return f"{self.titulo} — {self.instituicao}"

    def clean(self):
        super().clean()
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError(
                {"data_fim": "A data de fim não pode ser anterior à data de início."}
            )


class MakingOf(models.Model):
    class Fase(models.TextChoices):
        MODELO = "modelo", "Modelação"
        IMPLEMENTACAO = "implementacao", "Implementação"
        TESTE = "teste", "Testes"
        REVISAO = "revisao", "Revisão"

    titulo = models.CharField(max_length=150)
    data = models.DateField(auto_now_add=True)
    fase = models.CharField(max_length=20, choices=Fase.choices)
    descricao = models.TextField(verbose_name="trabalho realizado")
    decisoes = models.TextField(verbose_name="decisões e justificações")
    erros = models.TextField(blank=True)
    correcoes = models.TextField(blank=True, verbose_name="correções")
    uso_ia = models.TextField(
        blank=True,
        verbose_name="utilização de IA",
        help_text="Descrever como a IA contribuiu, ou não, para esta etapa.",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"app_label": "portfolio"},
        verbose_name="tipo de entidade documentada",
    )
    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="ID da entidade documentada",
    )
    entidade_documentada = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "entrada do Making Of"
        verbose_name_plural = "entradas do Making Of"

    def __str__(self):
        return f"{self.data}: {self.titulo}"

    def clean(self):
        super().clean()
        if bool(self.content_type_id) != bool(self.object_id):
            raise ValidationError(
                "O tipo e o ID da entidade documentada devem ser preenchidos em conjunto."
            )
        if self.content_type_id and self.content_type.app_label != "portfolio":
            raise ValidationError(
                {"content_type": "Só podem ser documentadas entidades do portfólio."}
            )
        if self.content_type_id and self.object_id:
            model_class = self.content_type.model_class()
            if model_class is None or not model_class.objects.filter(pk=self.object_id).exists():
                raise ValidationError(
                    {"object_id": "Não existe uma entidade com este ID."}
                )


class EvidenciaMakingOf(models.Model):
    entrada = models.ForeignKey(
        MakingOf,
        on_delete=models.CASCADE,
        related_name="evidencias",
    )
    imagem = models.ImageField(upload_to="makingof/")
    legenda = models.CharField(max_length=200)
    ordem = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["entrada", "ordem"]
        verbose_name = "evidência do Making Of"
        verbose_name_plural = "evidências do Making Of"
        constraints = [
            models.UniqueConstraint(
                fields=["entrada", "ordem"],
                name="ordem_evidencia_unica_por_entrada",
            )
        ]

    def __str__(self):
        return f"{self.entrada.titulo} — evidência {self.ordem}"
