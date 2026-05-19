"""Formularios del módulo de reservaciones — MEC Solutions"""

from django import forms
from django.conf import settings

from apps.parques.models import Parque
from .models import Reservacion, TipoVisita


class ReservacionForm(forms.ModelForm):
    """
    Formulario de reservación (CU-08 — RF01.5).
    Campos: parque, fecha_inicio, fecha_termino, num_personas, tipo_visita.
    """

    class Meta:
        model  = Reservacion
        fields = ['parque', 'fecha_inicio', 'fecha_termino', 'num_personas', 'tipo_visita']
        widgets = {
            'fecha_inicio':  forms.DateInput(
                attrs={'type': 'date',
                       'min': f'{settings.FESTIVAL_ANIO}-0{settings.FESTIVAL_MES_INICIO}-01',
                       'max': f'{settings.FESTIVAL_ANIO}-0{settings.FESTIVAL_MES_FIN}-31'}
            ),
            'fecha_termino': forms.DateInput(
                attrs={'type': 'date',
                       'min': f'{settings.FESTIVAL_ANIO}-0{settings.FESTIVAL_MES_INICIO}-01',
                       'max': f'{settings.FESTIVAL_ANIO}-0{settings.FESTIVAL_MES_FIN}-31'}
            ),
            'num_personas': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Número de personas'}),
        }
        labels = {
            'parque':        'Parque seleccionado',
            'fecha_inicio':  'Fecha de inicio de la estancia',
            'fecha_termino': 'Fecha de término de la estancia',
            'num_personas':  'Número de personas',
            'tipo_visita':   'Tipo de visita',
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar parques activos
        self.fields['parque'].queryset = Parque.objects.filter(activo=True)

    def clean(self):
        cleaned_data  = super().clean()
        parque        = cleaned_data.get('parque')
        tipo_visita   = cleaned_data.get('tipo_visita')

        # Verificar que el parque ofrezca el tipo de visita seleccionado (RNF03)
        if parque and tipo_visita == TipoVisita.CABANA and not parque.tiene_cabanas:
            self.add_error('tipo_visita',
                           f'El parque "{parque.nombre}" no cuenta con cabañas. '
                           f'Solo puedes elegir camping.')
        return cleaned_data
