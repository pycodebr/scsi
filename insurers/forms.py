from django import forms

from .models import Insurer, LineOfBusiness


class InsurerForm(forms.ModelForm):

    class Meta:
        model = Insurer
        fields = ('name', 'cnpj', 'susep_code', 'email', 'phone', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LineOfBusinessForm(forms.ModelForm):

    class Meta:
        model = LineOfBusiness
        fields = ('name', 'code', 'category', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }