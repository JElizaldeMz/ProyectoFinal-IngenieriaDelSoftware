"""
Formularios del módulo de usuarios — MEC Solutions
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroClienteForm(UserCreationForm):
    """
    Formulario de registro del usuario cliente (RF01.1).
    Campos: nombre, apellidos, correo electrónico, contraseña.
    """

    nombre   = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu nombre'}),
    )
    apellido = forms.CharField(
        label='Apellido(s)',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tus apellidos'}),
    )
    email    = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Crea una contraseña'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña'}),
    )

    class Meta:
        model  = Usuario
        fields = ['nombre', 'apellido', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
