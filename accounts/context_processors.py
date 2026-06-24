def is_gestor(request):
    gestor = (
        request.user.is_authenticated
        and request.user.groups.filter(name='gestor-portfolio').exists()
    )
    return {'is_gestor': gestor}
