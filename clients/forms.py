from django import forms

from agents.models import Producer
from clients.models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'client_type',
            'name',
            'cpf_cnpj',
            'email',
            'phone',
            'secondary_phone',
            'birth_date',
            'address',
            'city',
            'state',
            'zip_code',
            'assigned_producer',
            'notes',
            'is_active',
        ]
        widgets = {
            'client_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'secondary_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_producer': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if brokerage:
            self.fields['assigned_producer'].queryset = Producer.objects.filter(
                brokerage=brokerage, is_active=True
            )
