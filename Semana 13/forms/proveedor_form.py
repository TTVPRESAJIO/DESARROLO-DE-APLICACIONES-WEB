# =====================================================================
#  Formulario del modulo PROVEEDORES
#  ---------------------------------------------------------------------
#  Valida los datos de las empresas que abastecen los equipos solares.
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


class ProveedorForm(FlaskForm):
    """Alta y edicion de un proveedor."""

    empresa = StringField(
        "Nombre de la empresa",
        validators=[
            DataRequired(message="Escribe el nombre de la empresa."),
            Length(min=3, max=100,
                   message="El nombre debe tener entre 3 y 100 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Proviento"},
    )

    contacto = StringField(
        "Persona de contacto",
        validators=[
            DataRequired(message="Indica con quien se coordina el pedido."),
            Length(min=3, max=80,
                   message="El contacto debe tener entre 3 y 80 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Ing. Pablo Naranjo"},
    )

    correo = StringField(
        "Correo electronico",
        validators=[
            DataRequired(message="Escribe el correo del proveedor."),
            Email(message="Revisa el formato del correo (ejemplo: ventas@empresa.com)."),
            Length(max=100, message="El correo no puede superar los 100 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: ventas@empresa.com"},
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
        render_kw={"placeholder": "Ej.: 022500000"},
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="Indica la ciudad del proveedor."),
            Length(min=3, max=60, message="La ciudad debe tener entre 3 y 60 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Quito"},
    )

    suministra = StringField(
        "Que suministra",
        validators=[
            DataRequired(message="Indica que productos suministra."),
            Length(min=5, max=200,
                   message="La descripcion debe tener entre 5 y 200 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Paneles, inversores y baterias"},
    )

    submit = SubmitField("Guardar proveedor")
