from django import forms # type: ignore
from .models import Mascota,Aerolinea,Raza

class LoginForm(forms.Form):
    correo = forms.EmailField()
    contraseña = forms.CharField(widget=forms.PasswordInput)

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'fecha_nacimiento', 'peso', 'tamaño', 'inf_medica', 'sexo', 'especie', 'raza', 'imagen', 'estado']

    def __init__(self, *args, **kwargs):
        especie_id = kwargs.pop('especie_id', None)
        super().__init__(*args, **kwargs)

        # Inicializamos razas vacías o filtradas según especie seleccionada
        if especie_id:
            self.fields['raza'].queryset = Raza.objects.filter(especie_id=especie_id)
        else:
            self.fields['raza'].queryset = Raza.objects.none()

        self.fields['fecha_nacimiento'].widget.attrs['max'] = str(forms.DateField().to_python(str(forms.DateField().clean(str(forms.fields.datetime.date.today())))))

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha and fecha > forms.fields.datetime.date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        return fecha

class AerolineaForm(forms.ModelForm):
    class Meta:
        model = Aerolinea
        fields = ['nombre', 'politicas']