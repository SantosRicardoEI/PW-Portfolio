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
