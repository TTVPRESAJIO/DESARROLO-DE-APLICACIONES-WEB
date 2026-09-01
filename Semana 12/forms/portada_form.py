# =====================================================================
#  Formularios de la PORTADA
#  ---------------------------------------------------------------------
#  La pagina principal tiene dos formularios publicos: la solicitud de
#  servicio y el mensaje de contacto. Al pasarlos a Flask-WTF, TODOS los
#  formularios del proyecto quedan validados en el servidor y protegidos
#  con CSRF, no solo los de los modulos internos.
#
#  Los nombres de campo llevan el prefijo sol_ y con_ para que las dos
#  clases puedan convivir en la misma pagina sin pisarse.
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Email

# Opciones compartidas (clave guardada -> texto que ve la persona)
CATEGORIAS_SOLICITUD = [
    ("", "Selecciona una opcion..."),
    ("instalacion",   "Instalacion de sistema solar"),
    ("internet",      "Internet sin apagones"),
    ("mantenimiento", "Mantenimiento de un sistema existente"),
    ("asesoria",      "Asesoria y cotizacion"),
]

ASUNTOS_CONTACTO = [
    ("", "Selecciona una opcion..."),
    ("consulta",   "Consulta sobre sistemas solares"),
    ("cotizacion", "Solicitud de cotizacion"),
    ("soporte",    "Soporte tecnico"),
    ("otro",       "Otro tema"),
]


class SolicitudForm(FlaskForm):
    """Solicitud de servicio enviada desde la portada."""

    # Permite saber cual de los dos formularios de la pagina se envio.
    formulario = HiddenField(default="solicitud")

    sol_nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="Escribe tu nombre para poder contactarte."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    sol_categoria = SelectField(
        "Tipo de servicio",
        validators=[DataRequired(message="Elige el tipo de servicio que necesitas.")],
        choices=CATEGORIAS_SOLICITUD,
    )

    sol_descripcion = TextAreaField(
        "Describe tu necesidad",
        validators=[
            DataRequired(message="Cuentanos brevemente que necesitas."),
            Length(min=10, max=500,
                   message="La descripcion debe tener entre 10 y 500 caracteres."),
        ],
    )

    submit = SubmitField("Registrar solicitud")


class ContactoForm(FlaskForm):
    """Mensaje enviado desde la seccion de contacto."""

    formulario = HiddenField(default="contacto")

    con_nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="Escribe tu nombre."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    con_correo = StringField(
        "Correo electronico",
        validators=[
            DataRequired(message="Necesitamos tu correo para responderte."),
            Email(message="Revisa el formato del correo (ejemplo: nombre@correo.com)."),
        ],
    )

    con_asunto = SelectField(
        "Motivo del mensaje",
        validators=[DataRequired(message="Elige el motivo de tu mensaje.")],
        choices=ASUNTOS_CONTACTO,
    )

    con_mensaje = TextAreaField(
        "Mensaje",
        validators=[
            DataRequired(message="Escribe tu mensaje."),
            Length(min=15, max=1000,
                   message="El mensaje debe tener entre 15 y 1000 caracteres."),
        ],
    )

    submit = SubmitField("Enviar mensaje")
