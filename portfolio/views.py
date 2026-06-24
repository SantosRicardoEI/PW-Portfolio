from django.shortcuts import render
from .models import Licenciatura, UnidadeCurricular, Tecnologia, Projeto, TFC


def licenciaturas_view(request):
    licenciaturas = Licenciatura.objects.prefetch_related('unidades_curriculares').all()
    return render(request, 'portfolio/licenciaturas.html', {'licenciaturas': licenciaturas})


def ucs_view(request):
    ucs = UnidadeCurricular.objects.select_related('licenciatura').prefetch_related('docentes').all()
    return render(request, 'portfolio/ucs.html', {'ucs': ucs})


def tecnologias_view(request):
    tecnologias = Tecnologia.objects.all()
    return render(request, 'portfolio/tecnologias.html', {'tecnologias': tecnologias})


def projetos_view(request):
    projetos = Projeto.objects.prefetch_related('tecnologias', 'unidades_curriculares').all()
    return render(request, 'portfolio/projetos.html', {'projetos': projetos})


def tfcs_view(request):
    tfcs = TFC.objects.prefetch_related('alunos', 'orientadores', 'areas').all()
    return render(request, 'portfolio/tfcs.html', {'tfcs': tfcs})
