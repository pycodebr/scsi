from django import forms
from django.forms import inlineformset_factory

from clients.models import Client
from insurers.models import Insurer, LineOfBusiness
from partners.models import Agent, Producer

from .models import CoveredItem, Endorsement, Policy, Proposal, Renewal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = (
            'client', 'insurer', 'line_of_business', 'producer', 'agent',
            'number', 'status', 'net_premium', 'total_premium', 'iof',
            'proposed_start_date', 'proposed_end_date',
            'payment_terms', 'notes',
        )
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'insurer': forms.Select(attrs={'class': 'form-control'}),
            'line_of_business': forms.Select(attrs={'class': 'form-control'}),
            'producer': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'net_premium': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_premium': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iof': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proposed_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proposed_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            self.fields['client'].queryset = Client.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['insurer'].queryset = Insurer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['line_of_business'].queryset = LineOfBusiness.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['producer'].queryset = Producer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=self.tenant, is_active=True)


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = (
            'policy_number', 'client', 'insurer', 'line_of_business',
            'producer', 'agent',
            'status', 'net_premium', 'total_premium', 'iof',
            'commission_rate', 'start_date', 'end_date', 'payment_info',
        )
        widgets = {
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'insurer': forms.Select(attrs={'class': 'form-control'}),
            'line_of_business': forms.Select(attrs={'class': 'form-control'}),
            'producer': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'net_premium': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_premium': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iof': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_info': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            self.fields['client'].queryset = Client.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['insurer'].queryset = Insurer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['line_of_business'].queryset = LineOfBusiness.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['producer'].queryset = Producer.objects.filter(brokerage=self.tenant, is_active=True)
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=self.tenant, is_active=True)


class GeneratePolicyForm(forms.Form):
    policy_number = forms.CharField(
        label='Número da apólice',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: APOL-2024-001'}),
    )


class CoveredItemForm(forms.ModelForm):
    class Meta:
        model = CoveredItem
        fields = ('item_type', 'description', 'identifier', 'insured_amount', 'attributes', 'coverages')
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'insured_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'attributes': forms.HiddenInput(),
            'coverages': forms.HiddenInput(),
        }


class ProposalSearchForm(forms.Form):
    q = forms.CharField(label='Buscar', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Número, cliente...',
    }))
    status = forms.ChoiceField(label='Status', required=False, choices=[('', 'Todos')] + Proposal.Status.choices,
                               widget=forms.Select(attrs={'class': 'form-control'}))


class PolicySearchForm(forms.Form):
    q = forms.CharField(label='Buscar', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Número, cliente...',
    }))
    status = forms.ChoiceField(label='Status', required=False, choices=[('', 'Todos')] + Policy.Status.choices,
                               widget=forms.Select(attrs={'class': 'form-control'}))


CoveredItemInlineFormSet = inlineformset_factory(
    Proposal,
    CoveredItem,
    form=CoveredItemForm,
    extra=1,
    can_delete=True,
    fields=('item_type', 'description', 'identifier', 'insured_amount', 'attributes', 'coverages'),
)


class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = (
            'policy',
            'endorsement_number',
            'type',
            'description',
            'premium_change',
            'effective_date',
            'status',
        )
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-control'}),
            'endorsement_number': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'premium_change': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            self.fields['policy'].queryset = Policy.objects.filter(
                brokerage=self.tenant,
            ).order_by('-created_at')


class EndorsementSearchForm(forms.Form):
    type = forms.ChoiceField(
        label='Tipo',
        required=False,
        choices=[('', 'Todos')] + Endorsement.Type.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'Todos')] + Endorsement.Status.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )


class RenewalForm(forms.ModelForm):
    class Meta:
        model = Renewal
        fields = ('policy', 'new_policy', 'status', 'due_date', 'notes')
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-control'}),
            'new_policy': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if self.tenant:
            self.fields['policy'].queryset = Policy.objects.filter(
                brokerage=self.tenant,
            ).order_by('-created_at')
            self.fields['new_policy'].queryset = Policy.objects.filter(
                brokerage=self.tenant,
            ).order_by('-created_at')


class RenewalSearchForm(forms.Form):
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'Todos')] + Renewal.Status.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )