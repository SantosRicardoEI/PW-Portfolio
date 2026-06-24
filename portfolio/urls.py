from django.urls import path
from . import views

urlpatterns = [
    path('licenciaturas/', views.licenciaturas_view, name='licenciaturas'),
    path('ucs/', views.ucs_view, name='ucs'),
    path('tecnologias/', views.tecnologias_view, name='tecnologias'),
    path('projetos/', views.projetos_view, name='projetos'),
    path('tfcs/', views.tfcs_view, name='tfcs'),
    path('competencias/', views.competencias_view, name='competencias'),
    path('formacoes/', views.formacoes_view, name='formacoes'),

    # Projeto CRUD
    path('projetos/criar/', views.projeto_criar, name='projeto_criar'),
    path('projetos/<int:id>/editar/', views.projeto_editar, name='projeto_editar'),
    path('projetos/<int:id>/apagar/', views.projeto_apagar, name='projeto_apagar'),

    # Tecnologia CRUD
    path('tecnologias/criar/', views.tecnologia_criar, name='tecnologia_criar'),
    path('tecnologias/<int:id>/editar/', views.tecnologia_editar, name='tecnologia_editar'),
    path('tecnologias/<int:id>/apagar/', views.tecnologia_apagar, name='tecnologia_apagar'),

    # Competencia CRUD
    path('competencias/criar/', views.competencia_criar, name='competencia_criar'),
    path('competencias/<int:id>/editar/', views.competencia_editar, name='competencia_editar'),
    path('competencias/<int:id>/apagar/', views.competencia_apagar, name='competencia_apagar'),

    # Formacao CRUD
    path('formacoes/criar/', views.formacao_criar, name='formacao_criar'),
    path('formacoes/<int:id>/editar/', views.formacao_editar, name='formacao_editar'),
    path('formacoes/<int:id>/apagar/', views.formacao_apagar, name='formacao_apagar'),

    # Sobre
    path('sobre/', views.sobre_view, name='sobre'),
    path('makingof/<int:id>/', views.makingof_detalhe, name='makingof_detalhe'),
]
