from django.shortcuts import render
from .models import Curso, Professor, Aluno


def cursos_view(request):
    cursos = Curso.objects.select_related('professor').prefetch_related('alunos').all()
    return render(request, 'escola/cursos.html', {'cursos': cursos})


def professores_view(request):
    professores = Professor.objects.prefetch_related('cursos').all()
    return render(request, 'escola/professores.html', {'professores': professores})


def alunos_view(request):
    alunos = Aluno.objects.prefetch_related('cursos').all()
    return render(request, 'escola/alunos.html', {'alunos': alunos})


def curso_view(request, id):
    curso = Curso.objects.select_related('professor').prefetch_related('alunos').get(id=id)
    return render(request, 'escola/curso.html', {'curso': curso})
