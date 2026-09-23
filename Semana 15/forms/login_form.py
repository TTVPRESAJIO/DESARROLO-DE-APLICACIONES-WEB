# =====================================================================
#  Formulario de INICIO DE SESION  (Semana 14)
#  ---------------------------------------------------------------------
#  Aqui la validacion solo comprueba que los campos vengan completos.
#  Que las credenciales sean correctas o no se decide en la ruta,
#  consultando la base de datos con check_password_hash().
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Credenciales para entrar al sistema."""

    usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="Escribe tu nombre de usuario."),
            Length(min=3, max=50, message="El usuario tiene entre 3 y 50 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: admin", "autocomplete": "username",
                   "autofocus": True},
    )

    # PasswordField pinta un <input type="password">: el navegador oculta
    # lo escrito y no lo guarda en el historial del formulario.
    password = PasswordField(
        "Contrasena",
        validators=[DataRequired(message="Escribe tu contrasena.")],
        render_kw={"placeholder": "Tu contrasena",
                   "autocomplete": "current-password"},
    )

    recordarme = BooleanField("Mantener la sesion iniciada")

    submit = SubmitField("Iniciar sesion")
