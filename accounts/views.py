from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import MagicLinkForm, RegistoForm
from .models import MagicLinkToken


def _safe_next_url(request, default='projetos'):
    destination = request.POST.get('next') or request.GET.get('next')
    if destination and url_has_allowed_host_and_scheme(
        destination,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destination
    return reverse(default)


def _login_with_like_merge(request, user):
    old_session_key = request.session.session_key
    login(request, user)
    if old_session_key:
        from artigos.services import transferir_likes_da_sessao

        transferir_likes_da_sessao(old_session_key, user)


def _unique_username_for_email(email):
    base = email[:150]
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        tail = f'-{suffix}'
        username = f'{base[:150 - len(tail)]}{tail}'
        suffix += 1
    return username


def login_view(request):
    erro = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            _login_with_like_merge(request, user)
            return redirect(_safe_next_url(request))
        else:
            erro = 'Credenciais inválidas.'
    return render(
        request,
        'accounts/login.html',
        {'erro': erro, 'next': _safe_next_url(request)},
    )


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def registo_view(request):
    form = RegistoForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            user = form.save()
            grupo, _ = Group.objects.get_or_create(name='autores')
            user.groups.add(grupo)
        _login_with_like_merge(request, user)
        return redirect('artigos_lista')
    return render(request, 'accounts/registo.html', {'form': form})


def magic_link_pedido(request):
    mensagem = None
    form = MagicLinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        token_obj = MagicLinkToken.criar(email)
        link = request.build_absolute_uri(
            reverse('magic_link_verificar', args=[token_obj.token])
        )
        send_mail(
            subject='O teu link de acesso',
            message=f'Clica aqui para entrar:\n\n{link}\n\nVálido por 15 minutos.',
            from_email='noreply@portfolio.local',
            recipient_list=[email],
        )
        mensagem = 'Se o email for válido, receberás um link de acesso.'
    return render(
        request,
        'accounts/magic_link.html',
        {'mensagem': mensagem, 'form': form},
    )


def magic_link_verificar(request, token):
    with transaction.atomic():
        token_obj = get_object_or_404(
            MagicLinkToken.objects.select_for_update(), token=token
        )
        if not token_obj.is_valido():
            return render(request, 'accounts/magic_link_invalido.html')

        token_obj.usado = True
        token_obj.save(update_fields=['usado'])

        user = User.objects.filter(email__iexact=token_obj.email).first()
        if user is None:
            user = User(
                username=_unique_username_for_email(token_obj.email),
                email=token_obj.email,
            )
            user.set_unusable_password()
            user.save()

        grupo, _ = Group.objects.get_or_create(name='autores')
        user.groups.add(grupo)

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    _login_with_like_merge(request, user)
    return redirect('projetos')
