from django.urls import path
from . import views

urlpatterns = [
    path('', views.artigos_lista, name='artigos_lista'),
    path('criar/', views.artigo_criar, name='artigo_criar'),
    path('<int:id>/editar/', views.artigo_editar, name='artigo_editar'),
    path('<int:id>/apagar/', views.artigo_apagar, name='artigo_apagar'),
    path('<int:id>/like/', views.artigo_like, name='artigo_like'),
    path('<int:id>/comentar/', views.comentario_criar, name='comentario_criar'),
]
