from django import forms

from .models import Brokerage


class BrokerageOnboardingForm(forms.ModelForm):
    """Formulário de onboarding — CNPJ e razão social obrigatórios."""

    class Meta:
        model = Brokerage
        fields = ('legal_name', 'trade_name', 'cnpj', 'susep_code', 'email', 'phone')
        widgets = {
            'legal_name': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data['cnpj']
        digits = ''.join(c for c in cnpj if c.isdigit())
        if len(digits) != 14:
            raise forms.ValidationError('CNPJ deve conter 14 dígitos.')
        return cnpj