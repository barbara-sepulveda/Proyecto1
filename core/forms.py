
from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


ROL_CHOICES = [
    ("Administrador", "Administrador"),
    ("Dirección", "Dirección"),
    ("Departamento", "Departamento"),
    ("Jefe de Cuadrilla", "Jefe de Cuadrilla"),
    ("Territorial", "Territorial"),
]


def validar_email_unico_ci(value: str):
    """
    Valida unicidad de email sin distinguir may/min (case-insensitive).
    """
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError(
            "Ya existe un usuario con este correo (no distingue mayúsculas/minúsculas)."
        )


class UsuarioCrearForm(forms.ModelForm):
    """
    Formulario de creación de usuario con password y asignación de rol (grupo).
    """
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=True,
        min_length=8,
        help_text="Mínimo 8 caracteres.",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=True,
    )
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=True, label="Rol (grupo)")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
        widgets = {
            "is_active": forms.CheckboxInput(),
            "is_staff": forms.CheckboxInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise ValidationError("El correo es obligatorio.")
        validar_email_unico_ci(email)
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash seguro
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Asignación de grupo (rol)
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=self.cleaned_data["rol"])
            user.groups.add(group)
        return user


class UsuarioEditarForm(forms.ModelForm):
    """
    Edición de usuario con cambio opcional de contraseña y rol.
    """
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        min_length=8,
        help_text="Déjalo en blanco si no deseas cambiarla.",
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=False,
    )
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=True, label="Rol (grupo)")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
        help_texts = {
            "is_active": "Si está desmarcado, el usuario no podrá iniciar sesión (bloqueado).",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        groups = list(self.instance.groups.values_list("name", flat=True))
        if groups:
            self.fields["rol"].initial = groups[0]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise ValidationError("El correo es obligatorio.")
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                "Ya existe un usuario con este correo (no distingue mayúsculas/minúsculas)."
            )
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 or p2:
            if not p1 or not p2:
                self.add_error("password2", "Debes completar ambas contraseñas si vas a cambiarla.")
            elif p1 != p2:
                self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get("password1")
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=self.cleaned_data["rol"])
            user.groups.add(group)
        return user


class UsuarioToggleActivoForm(forms.Form):
    """
    Formulario simple de confirmación para activar/desactivar (bloquear/desbloquear)
    un usuario. No modifica datos por sí mismo; solo sirve para la vista de confirmación.
    """
    confirmar = forms.BooleanField(
        required=True,
        label="Confirmo el cambio de estado",
        help_text="Esta acción cambiará la disponibilidad del usuario para iniciar sesión.",
    )

    def next_state_label(self, user: User) -> str:
        """
        Devuelve el texto que corresponde a la acción que se va a realizar,
        útil para el template (activar o desactivar).
        """
        return "Desactivar" if user.is_active else "Activar"
