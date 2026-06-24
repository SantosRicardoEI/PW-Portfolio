from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registo/', views.registo_view, name='registo'),
    path('magic/', views.magic_link_pedido, name='magic_link_pedido'),
    path('magic/<str:token>/', views.magic_link_verificar, name='magic_link_verificar'),
]
