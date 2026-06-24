from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import group_required
from .models import Licenciatura, UnidadeCurricular, Tecnologia, Projeto, TFC, Competencia, Formacao, MakingOf
from .forms import ProjetoForm, TecnologiaForm, CompetenciaForm, FormacaoForm


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


# --- Projeto CRUD ---

@group_required('gestor-portfolio')
def projeto_criar(request):
    form = ProjetoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('projetos')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': 'Novo Projeto'})


@group_required('gestor-portfolio')
def projeto_editar(request, id):
    projeto = get_object_or_404(Projeto, id=id)
    form = ProjetoForm(request.POST or None, request.FILES or None, instance=projeto)
    if form.is_valid():
        form.save()
        return redirect('projetos')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': f'Editar: {projeto.titulo}'})


@group_required('gestor-portfolio')
def projeto_apagar(request, id):
    projeto = get_object_or_404(Projeto, id=id)
    if request.method == 'POST':
        projeto.delete()
        return redirect('projetos')
    return render(request, 'portfolio/confirmar_apagar.html', {'objeto': projeto, 'cancelar_url': 'projetos'})


# --- Tecnologia CRUD ---

@group_required('gestor-portfolio')
def tecnologia_criar(request):
    form = TecnologiaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('tecnologias')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': 'Nova Tecnologia'})


@group_required('gestor-portfolio')
def tecnologia_editar(request, id):
    tecnologia = get_object_or_404(Tecnologia, id=id)
    form = TecnologiaForm(request.POST or None, request.FILES or None, instance=tecnologia)
    if form.is_valid():
        form.save()
        return redirect('tecnologias')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': f'Editar: {tecnologia.nome}'})


@group_required('gestor-portfolio')
def tecnologia_apagar(request, id):
    tecnologia = get_object_or_404(Tecnologia, id=id)
    if request.method == 'POST':
        tecnologia.delete()
        return redirect('tecnologias')
    return render(request, 'portfolio/confirmar_apagar.html', {'objeto': tecnologia, 'cancelar_url': 'tecnologias'})


# --- Competencia CRUD ---

@group_required('gestor-portfolio')
def competencia_criar(request):
    form = CompetenciaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('competencias')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': 'Nova Competência'})


@group_required('gestor-portfolio')
def competencia_editar(request, id):
    competencia = get_object_or_404(Competencia, id=id)
    form = CompetenciaForm(request.POST or None, instance=competencia)
    if form.is_valid():
        form.save()
        return redirect('competencias')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': f'Editar: {competencia.nome}'})


@group_required('gestor-portfolio')
def competencia_apagar(request, id):
    competencia = get_object_or_404(Competencia, id=id)
    if request.method == 'POST':
        competencia.delete()
        return redirect('competencias')
    return render(request, 'portfolio/confirmar_apagar.html', {'objeto': competencia, 'cancelar_url': 'competencias'})


def competencias_view(request):
    competencias = Competencia.objects.all()
    return render(request, 'portfolio/competencias.html', {'competencias': competencias})


# --- Formacao CRUD ---

@group_required('gestor-portfolio')
def formacao_criar(request):
    form = FormacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('formacoes')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': 'Nova Formação'})


@group_required('gestor-portfolio')
def formacao_editar(request, id):
    formacao = get_object_or_404(Formacao, id=id)
    form = FormacaoForm(request.POST or None, request.FILES or None, instance=formacao)
    if form.is_valid():
        form.save()
        return redirect('formacoes')
    return render(request, 'portfolio/form.html', {'form': form, 'titulo': f'Editar: {formacao.titulo}'})


@group_required('gestor-portfolio')
def formacao_apagar(request, id):
    formacao = get_object_or_404(Formacao, id=id)
    if request.method == 'POST':
        formacao.delete()
        return redirect('formacoes')
    return render(request, 'portfolio/confirmar_apagar.html', {'objeto': formacao, 'cancelar_url': 'formacoes'})


def formacoes_view(request):
    formacoes = Formacao.objects.all()
    return render(request, 'portfolio/formacoes.html', {'formacoes': formacoes})


def makingof_detalhe(request, id):
    entrada = get_object_or_404(MakingOf, id=id)
    return render(request, 'portfolio/makingof_detalhe.html', {'entrada': entrada})


def sobre_view(request):
    projeto_portfolio = Projeto.objects.prefetch_related('tecnologias__tipo').filter(titulo='Portfolio de Programação Web').first()
    makingof = MakingOf.objects.all()
    return render(request, 'portfolio/sobre.html', {'projeto': projeto_portfolio, 'makingof': makingof})
