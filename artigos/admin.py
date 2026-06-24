from django.contrib import admin
from .models import Artigo, Comentario, LikeArtigo

admin.site.register(Artigo)
admin.site.register(Comentario)
admin.site.register(LikeArtigo)
