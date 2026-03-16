from django import forms

from agents.models import Agent, Producer


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            'agent_type', 'name', 'cpf_cnpj', 'susep_code',
            'email', 'phone', 'address', 'city', 'state',
            'zip_code', 'commission_rate', 'notes', 'is_active',
        ]
        widgets = {
            'agent_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = [
            'agent', 'name', 'cpf', 'susep_code',
            'email', 'phone', 'commission_rate', 'notes', 'is_active',
        ]
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if brokerage:
            self.fields['agent'].queryset = Agent.objects.filter(
                brokerage=brokerage, is_active=True
            )
