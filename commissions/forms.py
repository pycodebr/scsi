from django import forms
from .models import Commission, CommissionSplit


class CommissionStatusForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class CommissionSplitForm(forms.ModelForm):
    class Meta:
        model = CommissionSplit
        fields = (
            'beneficiary_type', 'agent', 'producer', 'rate', 'amount', 'status',
        )
        widgets = {
            'beneficiary_type': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'producer': forms.Select(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            from partners.models import Agent, Producer
            self.fields['agent'].queryset = Agent.objects.filter(
                brokerage=self.tenant, is_active=True,
            )
            self.fields['producer'].queryset = Producer.objects.filter(
                brokerage=self.tenant, is_active=True,
            )


class CommissionSearchForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + Commission.Status.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )