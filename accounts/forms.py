from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistoForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este email.')
        return email


class MagicLinkForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()
