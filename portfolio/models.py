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
    descricao = models.TextField()
    duracao_semestres = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    ects = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    website = models.URLField(blank=True)
    imagem = models.ImageField(upload_to="licenciaturas/", blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "licenciatura"
        verbose_name_plural = "licenciaturas"

    def __str__(self):
        return f"{self.sigla} — {self.nome}"


class Docente(models.Model):
    """Entidade adicional que evita repetir docentes em cada UC e TFC."""

    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    pagina_pessoal = models.URLField(
        help_text="Ligação para a página pessoal no site da Universidade Lusófona."
    )
    fotografia = models.ImageField(upload_to="docentes/", blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "docente"
        verbose_name_plural = "docentes"

    def __str__(self):
        return self.nome


class UnidadeCurricular(models.Model):
    """Unidade curricular pertencente a uma licenciatura."""

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
    semestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2)]
    )
    ects = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0.5)],
    )
    descricao = models.TextField()
    imagem = models.ImageField(upload_to="unidades_curriculares/")

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
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    descricao = models.TextField()
    logo = models.ImageField(upload_to="tecnologias/")
    website = models.URLField(help_text="Website oficial da tecnologia.")
    interesse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Classificação pessoal entre 1 e 5.",
    )
    nivel = models.CharField(max_length=15, choices=Nivel.choices)

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


class TFC(models.Model):
    """Modelação inicial, a rever quando o JSON de 2025 for analisado."""

    titulo = models.CharField(max_length=200)
    resumo = models.TextField()
    ano = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    estudante = models.CharField(max_length=150)
    orientadores = models.ManyToManyField(
        Docente,
        related_name="tfcs_orientados",
        blank=True,
    )
    area = models.CharField(max_length=100)
    url = models.URLField(blank=True, verbose_name="ligação externa")
    interesse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Classificação pessoal entre 1 e 5.",
    )
    destaque = models.BooleanField(default=False)

    class Meta:
        ordering = ["-ano", "titulo"]
        verbose_name = "TFC"
        verbose_name_plural = "TFCs"

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
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {"data_fim": "A data de fim não pode ser anterior à data de início."}
            )
