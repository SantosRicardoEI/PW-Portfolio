from django.contrib import admin
from .models import Curso, Professor, Aluno

admin.site.register(Aluno)
admin.site.register(Professor)


class CursoAdmin(admin.ModelAdmin):
    filter_horizontal = ('alunos',)

admin.site.register(Curso, CursoAdmin)
