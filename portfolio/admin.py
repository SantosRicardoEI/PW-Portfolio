from django.contrib import admin

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


admin.site.site_header = "Administração do Portfólio"
admin.site.site_title = "Portfólio"
admin.site.index_title = "Gestão de conteúdos"


@admin.register(Licenciatura)
class LicenciaturaAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "codigo", "duracao_semestres", "ects")
    search_fields = ("nome", "sigla", "codigo", "descricao")
    ordering = ("nome",)


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo", "pagina_pessoal")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")
    ordering = ("nome",)


@admin.register(UnidadeCurricular)
class UnidadeCurricularAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "licenciatura", "ano", "semestre", "ects")
    list_filter = ("licenciatura", "ano", "semestre")
    search_fields = ("nome", "codigo", "descricao")
    autocomplete_fields = ("licenciatura", "docentes")
    ordering = ("licenciatura", "ano", "semestre", "nome")


@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "nivel", "interesse", "website")
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


@admin.register(TFC)
class TFCAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estudante", "ano", "area", "interesse", "destaque")
    list_filter = ("ano", "area", "interesse", "destaque")
    search_fields = ("titulo", "resumo", "estudante", "area")
    autocomplete_fields = ("orientadores",)
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
