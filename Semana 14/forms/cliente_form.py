# =====================================================================
#  Formulario del modulo CLIENTES
#  ---------------------------------------------------------------------
#  Valida los datos de contacto de un cliente (persona o negocio).
#  Se reutiliza tanto para registrar como para editar.
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


class ClienteForm(FlaskForm):
    """Alta y edicion de un cliente de Electric Life."""

    nombre = StringField(
        "Nombre o razon social",
        validators=[
            DataRequired(message="Escribe el nombre del cliente."),
            Length(min=3, max=120,
                   message="El nombre debe tener entre 3 y 120 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Farmacia Su Salud"},
    )

    cedula = StringField(
        "Cedula o RUC",
        validators=[
            DataRequired(message="Escribe la cedula o el RUC."),
            Length(min=10, max=13,
                   message="La cedula tiene 10 digitos y el RUC 13."),
            Regexp(r"^\d+$", message="Solo se admiten numeros, sin guiones ni espacios."),
        ],
        render_kw={"placeholder": "Ej.: 1690012345001", "inputmode": "numeric"},
    )

    correo = StringField(
        "Correo electronico",
        validators=[
            DataRequired(message="Escribe el correo del cliente."),
            Email(message="Revisa el formato del correo (ejemplo: nombre@correo.com)."),
            Length(max=100, message="El correo no puede superar los 100 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: contacto@correo.com"},
    )

    telefono = StringField(
        "Telefono",
        validators=[
            DataRequired(message="Escribe un numero de telefono."),
            Length(min=7, max=15,
                   message="El telefono debe tener entre 7 y 15 digitos."),
            Regexp(r"^[\d\s+()-]+$",
                   message="Solo se admiten numeros y los signos + ( ) -"),
        ],
        render_kw={"placeholder": "Ej.: 0997327168"},
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="Indica la ciudad del cliente."),
            Length(min=3, max=60, message="La ciudad debe tener entre 3 y 60 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Puyo"},
    )

    estado = SelectField(
        "Estado",
        validators=[DataRequired(message="Elige el estado del cliente.")],
        choices=[
            ("", "Selecciona un estado..."),
            ("Activo", "Activo"),
            ("Inactivo", "Inactivo"),
        ],
    )

    submit = SubmitField("Guardar cliente")
