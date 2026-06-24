from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.views.decorators.http import require_POST

from accounts.decorators import group_required

from .models import Artigo, Comentario, LikeArtigo
from .forms import ArtigoForm, ComentarioForm


def artigos_lista(request):
    artigos = list(
        Artigo.objects.select_related('autor')
        .prefetch_related(
            Prefetch(
                'comentarios',
                queryset=Comentario.objects.select_related('autor'),
            )
        )
        .annotate(total_likes=Count('likes', distinct=True))
    )

    if request.user.is_authenticated:
        liked_ids = set(
            LikeArtigo.objects.filter(utilizador=request.user).values_list(
                'artigo_id', flat=True
            )
        )
    elif request.session.session_key:
        liked_ids = set(
            LikeArtigo.objects.filter(
                utilizador__isnull=True,
                session_key=request.session.session_key,
            ).values_list('artigo_id', flat=True)
        )
    else:
        liked_ids = set()

    for artigo in artigos:
        artigo.gostado_pelo_visitante = artigo.id in liked_ids

    return render(request, 'artigos/lista.html', {'artigos': artigos})


@group_required('autores')
def artigo_criar(request):
    form = ArtigoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        artigo = form.save(commit=False)
        artigo.autor = request.user
        artigo.save()
        return redirect('artigos_lista')
    return render(request, 'artigos/form.html', {'form': form, 'titulo': 'Novo Artigo'})


@group_required('autores')
def artigo_editar(request, id):
    artigos = Artigo.objects.all()
    if not request.user.is_superuser:
        artigos = artigos.filter(autor=request.user)
    artigo = get_object_or_404(artigos, id=id)
    form = ArtigoForm(request.POST or None, request.FILES or None, instance=artigo)
    if form.is_valid():
        form.save()
        return redirect('artigos_lista')
    return render(request, 'artigos/form.html', {'form': form, 'titulo': 'Editar Artigo'})


@group_required('autores')
def artigo_apagar(request, id):
    artigos = Artigo.objects.all()
    if not request.user.is_superuser:
        artigos = artigos.filter(autor=request.user)
    artigo = get_object_or_404(artigos, id=id)
    if request.method == 'POST':
        artigo.delete()
        return redirect('artigos_lista')
    return render(request, 'artigos/confirmar_apagar.html', {'artigo': artigo})


@require_POST
def artigo_like(request, id):
    artigo = get_object_or_404(Artigo, id=id)

    if request.user.is_authenticated:
        if request.session.session_key:
            LikeArtigo.objects.filter(
                artigo=artigo,
                utilizador__isnull=True,
                session_key=request.session.session_key,
            ).delete()
        lookup = {'artigo': artigo, 'utilizador': request.user}
    else:
        if not request.session.session_key:
            request.session.create()
        lookup = {
            'artigo': artigo,
            'utilizador': None,
            'session_key': request.session.session_key,
        }

    like = LikeArtigo.objects.filter(**lookup).first()
    if like:
        like.delete()
    else:
        LikeArtigo.objects.create(**lookup)
    return redirect('artigos_lista')


@login_required
@require_POST
def comentario_criar(request, id):
    artigo = get_object_or_404(Artigo, id=id)
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.artigo = artigo
        comentario.autor = request.user
        comentario.save()
    return redirect('artigos_lista')
