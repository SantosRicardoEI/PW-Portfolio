from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Artigo, Comentario
from .forms import ArtigoForm, ComentarioForm


def artigos_lista(request):
    artigos = Artigo.objects.prefetch_related('likes', 'comentarios', 'autor').all()
    return render(request, 'artigos/lista.html', {'artigos': artigos})


@login_required
def artigo_criar(request):
    if not request.user.groups.filter(name='autores').exists():
        return redirect('artigos_lista')
    form = ArtigoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        artigo = form.save(commit=False)
        artigo.autor = request.user
        artigo.save()
        return redirect('artigos_lista')
    return render(request, 'artigos/form.html', {'form': form, 'titulo': 'Novo Artigo'})


@login_required
def artigo_editar(request, id):
    artigo = get_object_or_404(Artigo, id=id)
    if artigo.autor != request.user:
        return redirect('artigos_lista')
    form = ArtigoForm(request.POST or None, request.FILES or None, instance=artigo)
    if form.is_valid():
        form.save()
        return redirect('artigos_lista')
    return render(request, 'artigos/form.html', {'form': form, 'titulo': 'Editar Artigo'})


@login_required
def artigo_apagar(request, id):
    artigo = get_object_or_404(Artigo, id=id)
    if artigo.autor != request.user:
        return redirect('artigos_lista')
    if request.method == 'POST':
        artigo.delete()
        return redirect('artigos_lista')
    return render(request, 'artigos/confirmar_apagar.html', {'artigo': artigo})


@login_required
def artigo_like(request, id):
    artigo = get_object_or_404(Artigo, id=id)
    if request.user in artigo.likes.all():
        artigo.likes.remove(request.user)
    else:
        artigo.likes.add(request.user)
    return redirect('artigos_lista')


@login_required
def comentario_criar(request, id):
    artigo = get_object_or_404(Artigo, id=id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.artigo = artigo
            comentario.autor = request.user
            comentario.save()
    return redirect('artigos_lista')
