from django import forms
from .models import Projeto, Tecnologia, Competencia, Formacao


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['titulo', 'descricao', 'conceitos_aplicados', 'data', 'imagem',
                  'github_url', 'demo_url', 'video_url', 'destaque',
                  'unidades_curriculares', 'tecnologias']


class TecnologiaForm(forms.ModelForm):
    class Meta:
        model = Tecnologia
        fields = ['nome', 'tipo', 'categoria', 'descricao', 'logo', 'website', 'interesse', 'nivel']


class CompetenciaForm(forms.ModelForm):
    class Meta:
        model = Competencia
        fields = ['nome', 'categoria', 'descricao', 'nivel', 'projetos', 'tecnologias']


class FormacaoForm(forms.ModelForm):
    class Meta:
        model = Formacao
        fields = ['titulo', 'instituicao', 'tipo', 'data_inicio', 'data_fim',
                  'em_curso', 'descricao', 'certificado', 'url', 'competencias']
