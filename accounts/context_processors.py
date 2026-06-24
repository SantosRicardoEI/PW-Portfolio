def is_gestor(request):
    authenticated = request.user.is_authenticated
    superuser = authenticated and request.user.is_superuser
    gestor = authenticated and (
        superuser or request.user.groups.filter(name='gestor-portfolio').exists()
    )
    autor = authenticated and (
        superuser or request.user.groups.filter(name='autores').exists()
    )
    return {'is_gestor': gestor, 'is_autor': autor}
