from django import forms
from .models import Producto,Categoria, PrecioCompra
from django.contrib.auth.models import User,Group
from django.contrib.auth.forms import UserCreationForm


class ProductoForm(forms.ModelForm):
    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    # Aquí va el resto igual, incluyendo nuevas_categorias y fecha_vencimiento

    fecha_vencimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    nuevas_categorias = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Ingrese nuevas categorías separadas por coma (solo admins)"
    )

    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'cantidad', 'ubicacion', 'fecha_vencimiento', 'categorias']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            # 'categorias': forms.CheckboxSelectMultiple(),  <-- Ya está definido arriba en el campo explícito
        }



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Rol / Perfil",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'group']



class PrecioCompraForm(forms.ModelForm):
    class Meta:
        model = PrecioCompra
        fields = ['producto', 'precio', 'fecha_compra']
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'producto': forms.HiddenInput(),  # Para cuando uses el formulario desde el detalle del producto
        }


class ReporteInventarioForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha inicio"
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha fin"
    )
    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Categorías"
    )