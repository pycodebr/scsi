from django import forms
from .models import Agent, Producer


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = (
            'entity_type', 'name', 'document', 'email', 'phone',
            'susep_code', 'user', 'default_commission_rate', 'is_active',
        )
        widgets = {
            'entity_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'default_commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            from accounts.models import User
            self.fields['user'].queryset = User.objects.filter(
                brokerage=self.tenant, is_active=True,
            )


class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = (
            'agent', 'entity_type', 'name', 'document', 'email', 'phone',
            'user', 'default_commission_rate', 'is_active',
        )
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'entity_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'default_commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            from accounts.models import User
            self.fields['agent'].queryset = Agent.objects.filter(
                brokerage=self.tenant, is_active=True,
            )
            self.fields['user'].queryset = User.objects.filter(
                brokerage=self.tenant, is_active=True,
            )