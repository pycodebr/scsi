from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from .models import User


class UserRegistrationForm(UserCreationForm):
    """Cadastro básico de usuário (nome + e-mail + senha)."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class EmailAuthenticationForm(AuthenticationForm):
    """Login por e-mail (o campo ``username`` recebe o e-mail)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'E-mail'
        self.fields['username'].widget = forms.EmailInput(
            attrs={'class': 'form-control', 'autofocus': True, 'autocomplete': 'email'}
        )
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class CustomPasswordResetForm(PasswordResetForm):
    """Recuperação de senha com e-mail estilizado."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(
            attrs={'class': 'form-control', 'autofocus': True, 'autocomplete': 'email'}
        )


class CustomSetPasswordForm(SetPasswordForm):
    """Redefinição de senha com campos estilizados."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control', 'autofocus': True, 'autocomplete': 'new-password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control', 'autocomplete': 'new-password',
        })


class UserProfileForm(forms.ModelForm):
    """Edição dos dados do próprio usuário."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class MemberCreateForm(UserCreationForm):
    """Criação de membro dentro do tenant (owner/manager)."""

    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Papel',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        self.max_users = kwargs.pop('max_users', None)
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned = super().clean()
        if self.brokerage and self.max_users is not None:
            current = User.objects.filter(brokerage=self.brokerage, is_active=True).count()
            if current >= self.max_users:
                raise ValidationError(
                    f'Limite de {self.max_users} usuário(s) do plano atingido.'
                )
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.brokerage = self.brokerage
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class MemberUpdateForm(forms.ModelForm):
    """Atualização de membro dentro do tenant."""

    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Papel',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'is_active')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
