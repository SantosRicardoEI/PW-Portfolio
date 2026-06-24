from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from .forms import RegistoForm
from .models import MagicLinkToken


def login_view(request):
    erro = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('projetos')
        else:
            erro = 'Credenciais inválidas.'
    return render(request, 'accounts/login.html', {'erro': erro})


def logout_view(request):
    logout(request)
    return redirect('login')


def registo_view(request):
    form = RegistoForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        grupo, _ = Group.objects.get_or_create(name='autores')
        user.groups.add(grupo)
        login(request, user)
        return redirect('artigos_lista')
    return render(request, 'accounts/registo.html', {'form': form})


def magic_link_pedido(request):
    mensagem = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            token_obj = MagicLinkToken.criar(email)
            link = request.build_absolute_uri(f'/accounts/magic/{token_obj.token}/')
            send_mail(
                subject='O teu link de acesso',
                message=f'Clica aqui para entrar:\n\n{link}\n\nVálido por 15 minutos.',
                from_email='noreply@portfolio.local',
                recipient_list=[email],
            )
            mensagem = f'Link enviado para {email}. Verifica o terminal.'
    return render(request, 'accounts/magic_link.html', {'mensagem': mensagem})


def magic_link_verificar(request, token):
    token_obj = get_object_or_404(MagicLinkToken, token=token)
    if not token_obj.is_valido():
        return render(request, 'accounts/magic_link_invalido.html')
    token_obj.usado = True
    token_obj.save()
    # encontra ou cria o utilizador pelo email
    user, _ = User.objects.get_or_create(
        username=token_obj.email,
        defaults={'email': token_obj.email}
    )
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return redirect('projetos')
