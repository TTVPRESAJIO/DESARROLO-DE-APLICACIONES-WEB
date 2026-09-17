# =====================================================================
#  Formulario del modulo FACTURACION
#  ---------------------------------------------------------------------
#  Valida los comprobantes emitidos. Incluye un ejemplo de validacion
#  con expresion regular (el formato del numero de factura del SRI) y
#  una validacion personalizada escrita a mano.
# =====================================================================

from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Regexp, ValidationError


class FacturaForm(FlaskForm):
    """Alta y edicion de una factura."""

    numero = StringField(
        "Numero de factura",
        validators=[
            DataRequired(message="Escribe el numero de la factura."),
            Regexp(r"^\d{3}-\d{3}-\d{6,9}$",
                   message="Usa el formato del SRI: 001-001-000001"),
        ],
        render_kw={"placeholder": "Ej.: 001-001-000001"},
    )

    # -----------------------------------------------------------------
    #  Semana 13: clave foranea hacia la tabla clientes.
    #  Antes el cliente era texto libre; ahora se elige de la lista real
    #  de clientes registrados, de modo que la factura siempre apunta a
    #  un cliente que existe (integridad referencial).
    # -----------------------------------------------------------------
    id_cliente = SelectField(
        "Cliente",
        validators=[
            InputRequired(message="Indica a que cliente pertenece la factura."),
            NumberRange(min=1, message="Elige un cliente de la lista."),
        ],
        coerce=int,
        choices=[],
    )

    fecha = DateField(
        "Fecha de emision",
        validators=[DataRequired(message="Indica la fecha de emision.")],
        format="%Y-%m-%d",
    )

    total = DecimalField(
        "Total (USD)",
        places=2,
        validators=[
            InputRequired(message="Indica el total de la factura."),
            NumberRange(min=0.01, max=999999,
                        message="El total debe ser mayor que 0."),
        ],
        render_kw={"placeholder": "Ej.: 2730.00", "step": "0.01", "min": "0"},
    )

    estado = SelectField(
        "Estado",
        validators=[DataRequired(message="Elige el estado de la factura.")],
        choices=[
            ("", "Selecciona un estado..."),
            ("Pagada", "Pagada"),
            ("Pendiente", "Pendiente"),
            ("Anulada", "Anulada"),
        ],
    )

    submit = SubmitField("Guardar factura")

    # -----------------------------------------------------------------
    #  Validacion personalizada de WTForms.
    #  Un metodo llamado validate_<nombre_del_campo> se ejecuta ademas
    #  de los validadores de la lista.
    # -----------------------------------------------------------------
    def validate_fecha(self, campo):
        """Una factura no puede emitirse con fecha futura."""
        if campo.data and campo.data > date.today():
            raise ValidationError("La fecha no puede ser posterior a hoy.")
