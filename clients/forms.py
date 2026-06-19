from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    """Formulário de criação / edição de cliente."""

    class Meta:
        model = Client
        fields = (
            'person_type', 'name', 'trade_name', 'document', 'email', 'phone',
            'birth_date',
            'address_street', 'address_number', 'address_complement',
            'address_neighborhood', 'address_city', 'address_state', 'address_zip',
            'notes',
        )
        widgets = {
            'person_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address_street': forms.TextInput(attrs={'class': 'form-control'}),
            'address_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_complement': forms.TextInput(attrs={'class': 'form-control'}),
            'address_neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'address_city': forms.TextInput(attrs={'class': 'form-control'}),
            'address_state': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'address_zip': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClientSearchForm(forms.Form):
    """Busca na listagem de clientes."""
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome, documento ou e-mail...',
        }),
    )
    person_type = forms.ChoiceField(
        label='Tipo',
        required=False,
        choices=[('', 'Todos')] + Client.PersonType.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )