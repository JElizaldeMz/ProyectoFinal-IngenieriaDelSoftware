"""Formularios del módulo de parques — MEC Solutions"""

from django import forms
from .models import Parque


class ParqueForm(forms.ModelForm):
    """Formulario para crear y editar parques (CU-16, CU-17)."""

    class Meta:
        model  = Parque
        fields = [
            'nombre', 'direccional', 'servicios', 'horario',
            'latitud', 'longitud',
            'tiene_cabanas', 'cap_camping', 'cap_cabanas',
            'activo',
        ]
        widgets = {
            'nombre':      forms.TextInput(attrs={'placeholder': 'Nombre del parque'}),
            'direccional': forms.TextInput(attrs={'placeholder': 'Dirección completa'}),
            'servicios':   forms.Textarea(attrs={'rows': 3, 'placeholder': 'Servicios disponibles'}),
            'horario':     forms.TextInput(attrs={'placeholder': 'Ej: Lun–Dom 18:00–23:00'}),
            'latitud':     forms.NumberInput(attrs={'step': 'any', 'placeholder': '20.0000'}),
            'longitud':    forms.NumberInput(attrs={'step': 'any', 'placeholder': '-98.0000'}),
        }
        labels = {
            'direccional':  'Dirección',
            'tiene_cabanas': '¿El parque cuenta con cabañas?',
            'cap_camping':   'Capacidad máxima de camping (personas)',
            'cap_cabanas':   'Capacidad máxima de cabañas (personas)',
        }

    def clean(self):
        cleaned_data  = super().clean()
        tiene_cabanas = cleaned_data.get('tiene_cabanas')
        cap_cabanas   = cleaned_data.get('cap_cabanas', 0)

        if tiene_cabanas and cap_cabanas == 0:
            self.add_error('cap_cabanas',
                           'Si el parque tiene cabañas, debes indicar la capacidad máxima.')
        if not tiene_cabanas:
            cleaned_data['cap_cabanas'] = 0  # forzar a 0 si no tiene cabañas

        return cleaned_data
