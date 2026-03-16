from django import forms

from branches.models import InsuranceBranch
from coverages.models import CoverageType


class CoverageTypeForm(forms.ModelForm):
    class Meta:
        model = CoverageType
        fields = ['name', 'description', 'insurance_branch', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_branch': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if brokerage:
            self.fields['insurance_branch'].queryset = InsuranceBranch.objects.filter(
                brokerage=brokerage, is_active=True
            )
