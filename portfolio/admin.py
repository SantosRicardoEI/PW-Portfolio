from django.contrib import admin

from .models import (
    Aluno,
    AreaTFC,
    Competencia,
    Docente,
    EvidenciaMakingOf,
    Formacao,
    Licenciatura,
    MakingOf,
    PalavraChaveTFC,
    Projeto,
    Tecnologia,
    TFC,
    TipoTecnologia,
    UnidadeCurricular,
)


admin.site.site_header = "Administração do Portfólio"
admin.site.site_title = "Portfólio"
admin.site.index_title = "Gestão de conteúdos"


@admin.register(Licenciatura)
class LicenciaturaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "sigla",
        "codigo",
        "grau",
        "duracao_semestres",
        "ects",
        "modalidade",
    )
    list_filter = ("grau", "modalidade", "acreditacao")
    search_fields = (
        "nome",
        "sigla",
        "codigo",
        "descricao",
        "objetivos",
        "competencias",
        "saidas_profissionais",
    )
    autocomplete_fields = ("docentes",)
    ordering = ("nome",)


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("nome", "grau", "regime", "email", "ativo", "pagina_pessoal")
    list_filter = ("grau", "regime", "ativo")
    search_fields = ("nome", "nome_completo", "email", "orcid", "ciencia_vitae")
    ordering = ("nome",)


@admin.register(UnidadeCurricular)
class UnidadeCurricularAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "codigo",
        "licenciatura",
        "ano",
        "semestre",
        "ects",
        "ano_letivo",
    )
    list_filter = ("licenciatura", "ano", "semestre", "ano_letivo", "natureza")
    search_fields = (
        "nome",
        "codigo",
        "descricao",
        "apresentacao",
        "objetivos",
        "competencias",
        "programa",
        "bibliografia",
    )
    autocomplete_fields = ("licenciatura", "docentes")
    ordering = ("licenciatura", "ano", "semestre", "nome")


@admin.register(TipoTecnologia)
class TipoTecnologiaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "categoria", "nivel", "interesse", "website")
    list_filter = ("categoria", "nivel", "interesse")
    search_fields = ("nome", "descricao")
    ordering = ("nome",)


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data", "destaque", "github_url")
    list_filter = ("destaque", "data", "tecnologias")
    search_fields = ("titulo", "descricao", "conceitos_aplicados")
    autocomplete_fields = ("unidades_curriculares", "tecnologias")
    date_hierarchy = "data"
    ordering = ("-data", "titulo")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "numero")
    search_fields = ("nome", "numero")
    ordering = ("nome", "numero")


@admin.register(AreaTFC)
class AreaTFCAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(PalavraChaveTFC)
class PalavraChaveTFCAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(TFC)
class TFCAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "ano", "email", "interesse", "destaque")
    list_filter = (
        "estado",
        "ano",
        "licenciaturas",
        "areas",
        "interesse",
        "destaque",
    )
    search_fields = (
        "titulo",
        "resumo",
        "email",
        "alunos__nome",
        "alunos__numero",
        "orientadores__nome",
        "areas__nome",
        "palavras_chave__nome",
        "tecnologias__nome",
    )
    autocomplete_fields = (
        "alunos",
        "orientadores",
        "licenciaturas",
        "areas",
        "palavras_chave",
        "tecnologias",
    )
    ordering = ("-ano", "titulo")


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "nivel")
    list_filter = ("categoria", "nivel")
    search_fields = ("nome", "descricao")
    autocomplete_fields = ("projetos", "tecnologias")
    ordering = ("categoria", "nome")


@admin.register(Formacao)
class FormacaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "instituicao", "tipo", "data_inicio", "data_fim", "em_curso")
    list_filter = ("tipo", "em_curso", "instituicao")
    search_fields = ("titulo", "instituicao", "descricao")
    autocomplete_fields = ("competencias",)
    date_hierarchy = "data_inicio"
    ordering = ("-data_inicio", "titulo")


class EvidenciaMakingOfInline(admin.TabularInline):
    model = EvidenciaMakingOf
    extra = 1
    fields = ("imagem", "legenda", "ordem")
    ordering = ("ordem",)


@admin.register(MakingOf)
class MakingOfAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data", "fase", "entidade_associada")
    list_filter = ("fase", "data", "content_type")
    search_fields = ("titulo", "descricao", "decisoes", "erros", "correcoes", "uso_ia")
    readonly_fields = ("data", "entidade_associada")
    fieldsets = (
        (None, {"fields": ("titulo", "data", "fase")}),
        (
            "Entidade documentada",
            {"fields": ("content_type", "object_id", "entidade_associada")},
        ),
        (
            "Diário de bordo",
            {"fields": ("descricao", "decisoes", "erros", "correcoes", "uso_ia")},
        ),
    )
    inlines = (EvidenciaMakingOfInline,)
    ordering = ("-data", "-id")

    @admin.display(description="entidade documentada")
    def entidade_associada(self, obj):
        if obj is None or obj.entidade_documentada is None:
            return "—"
        return str(obj.entidade_documentada)


@admin.register(EvidenciaMakingOf)
class EvidenciaMakingOfAdmin(admin.ModelAdmin):
    list_display = ("legenda", "entrada", "ordem")
    list_filter = ("entrada__fase",)
    search_fields = ("legenda", "entrada__titulo")
    autocomplete_fields = ("entrada",)
    ordering = ("entrada", "ordem")
