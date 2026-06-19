from django import forms
from .models import Claim


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = (
            'policy',
            'covered_item',
            'claim_number',
            'occurrence_date',
            'notice_date',
            'status',
            'description',
            'claimed_amount',
            'approved_amount',
        )
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-control'}),
            'covered_item': forms.Select(attrs={'class': 'form-control'}),
            'claim_number': forms.TextInput(attrs={'class': 'form-control'}),
            'occurrence_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'claimed_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if self.brokerage:
            from insurance.models import Policy, CoveredItem
            self.fields['policy'].queryset = Policy.objects.filter(
                brokerage=self.brokerage,
            ).order_by('-created_at')
            policy_qs = Policy.objects.filter(brokerage=self.brokerage)
            self.fields['covered_item'].queryset = CoveredItem.objects.filter(
                policy__in=policy_qs,
            ).order_by('-created_at')
        if self.instance and self.instance.pk:
            self.fields['covered_item'].queryset = CoveredItem.objects.filter(
                policy=self.instance.policy,
            )

    def clean(self):
        cleaned_data = super().clean()
        covered_item = cleaned_data.get('covered_item')
        policy = cleaned_data.get('policy')
        if covered_item and policy:
            if covered_item.policy_id != policy.pk:
                self.add_error(
                    'covered_item',
                    'Item coberto não pertence à apólice selecionada.',
                )
        occurrence = cleaned_data.get('occurrence_date')
        notice = cleaned_data.get('notice_date')
        if occurrence and notice and occurrence > notice:
            self.add_error(
                'occurrence_date',
                'Data da ocorrência não pode ser posterior ao aviso.',
            )
        return cleaned_data


class ClaimSearchForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + Claim.Status.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    policy = forms.IntegerField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )