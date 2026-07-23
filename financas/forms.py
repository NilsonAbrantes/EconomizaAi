from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "seuemail@exemplo.com",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )


class CadastroUsuarioForm(UserCreationForm):
    nome = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Seu nome completo",
                "autocomplete": "name",
                "autofocus": True,
            }
        ),
    )
    email = forms.EmailField(
        label="E-mail",
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "seuemail@exemplo.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("nome", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Crie uma senha",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Repita a senha",
                "autocomplete": "new-password",
            }
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["nome"].strip()

        if commit:
            user.save()

        return user
