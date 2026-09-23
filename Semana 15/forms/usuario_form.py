# =====================================================================
#  Formulario de REGISTRO DE USUARIOS  (Semana 14)
#  ---------------------------------------------------------------------
#  Valida los datos antes de crear la cuenta. La contrasena se escribe
#  dos veces y WTForms comprueba que coincidan con EqualTo, para evitar
#  que alguien quede fuera de su cuenta por una errata. [Prevencion de
#  errores]
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp


class UsuarioForm(FlaskForm):
    """Alta de un usuario del sistema."""

    usuario = StringField(
        "Nombre de usuario",
        validators=[
            DataRequired(message="Elige un nombre de usuario."),
            Length(min=3, max=50,
                   message="El usuario debe tener entre 3 y 50 caracteres."),
            Regexp(r"^[A-Za-z0-9_.-]+$",
                   message="Solo se admiten letras, numeros y los signos . _ -"),
        ],
        render_kw={"placeholder": "Ej.: dallacuri", "autocomplete": "username"},
    )

    nombre_completo = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="Escribe tu nombre completo."),
            Length(min=3, max=120,
                   message="El nombre debe tener entre 3 y 120 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Daniel Allacuri", "autocomplete": "name"},
    )

    password = PasswordField(
        "Contrasena",
        validators=[
            DataRequired(message="Escribe una contrasena."),
            Length(min=6, max=100,
                   message="La contrasena debe tener al menos 6 caracteres."),
        ],
        render_kw={"placeholder": "Minimo 6 caracteres",
                   "autocomplete": "new-password"},
    )

    confirmar = PasswordField(
        "Repite la contrasena",
        validators=[
            DataRequired(message="Repite la contrasena."),
            EqualTo("password", message="Las dos contrasenas no coinciden."),
        ],
        render_kw={"placeholder": "Escribela otra vez",
                   "autocomplete": "new-password"},
    )

    submit = SubmitField("Crear cuenta")
