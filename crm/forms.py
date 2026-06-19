from django import forms
from .models import Deal, Pipeline, Stage


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = (
            'pipeline', 'stage', 'client', 'producer', 'agent',
            'line_of_business', 'insurer', 'proposal',
            'title', 'description', 'estimated_value',
            'status', 'expected_close_date',
        )
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'producer': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'line_of_business': forms.Select(attrs={'class': 'form-control'}),
            'insurer': forms.Select(attrs={'class': 'form-control'}),
            'proposal': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'expected_close_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            from clients.models import Client
            from insurers.models import Insurer, LineOfBusiness
            from partners.models import Agent, Producer
            from insurance.models import Proposal
            self.fields['client'].queryset = Client.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['producer'].queryset = Producer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['line_of_business'].queryset = LineOfBusiness.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['insurer'].queryset = Insurer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['proposal'].queryset = Proposal.objects.filter(brokerage=self.tenant)
            self.fields['pipeline'].queryset = Pipeline.objects.filter(brokerage=self.tenant)
            self.fields['stage'].queryset = Stage.objects.filter(pipeline__brokerage=self.tenant)


class PipelineForm(forms.ModelForm):
    class Meta:
        model = Pipeline
        fields = ('name', 'is_default')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ('pipeline', 'name', 'color', 'order', 'is_won', 'is_lost')
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_won': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_lost': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }