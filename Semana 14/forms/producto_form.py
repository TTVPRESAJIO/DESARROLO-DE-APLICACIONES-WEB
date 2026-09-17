# =====================================================================
#  Formulario del modulo PRODUCTOS
#  ---------------------------------------------------------------------
#  Hereda de FlaskForm, por lo que incorpora automaticamente el token
#  CSRF que se imprime en la plantilla con form.hidden_tag().
#
#  La misma clase se usa para REGISTRAR y para EDITAR: al editar se
#  crea el formulario con obj=producto y WTForms rellena los campos.
# =====================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    """Alta y edicion de un producto del catalogo solar."""

    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(message="Escribe el nombre del producto."),
            Length(min=3, max=120,
                   message="El nombre debe tener entre 3 y 120 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: Panel Solar Monocristalino 450W"},
    )

    categoria = SelectField(
        "Categoria",
        validators=[DataRequired(message="Elige una categoria.")],
        choices=[
            ("", "Selecciona una categoria..."),
            ("Panel Solar", "Panel Solar"),
            ("Inversor", "Inversor"),
            ("Bateria", "Bateria"),
            ("Regulador", "Regulador"),
            ("Proteccion", "Proteccion"),
            ("Cableado", "Cableado"),
            ("Estructura", "Estructura"),
        ],
    )

    precio = DecimalField(
        "Precio de venta (USD)",
        places=2,
        validators=[
            InputRequired(message="Indica el precio del producto."),
            NumberRange(min=0.01, max=99999,
                        message="El precio debe ser mayor que 0."),
        ],
        render_kw={"placeholder": "Ej.: 180.00", "step": "0.01", "min": "0"},
    )

    # Se usa InputRequired en lugar de DataRequired porque un stock de 0
    # es un valor valido, y DataRequired lo rechazaria por considerarlo vacio.
    stock = IntegerField(
        "Stock disponible",
        validators=[
            InputRequired(message="Indica cuantas unidades hay en stock."),
            NumberRange(min=0, message="El stock no puede ser negativo."),
        ],
        render_kw={"placeholder": "Ej.: 24", "min": "0"},
    )

    icono = StringField(
        "Icono (Bootstrap Icons)",
        validators=[
            Length(max=40, message="El icono no puede superar los 40 caracteres."),
        ],
        render_kw={"placeholder": "Ej.: bi-sun (opcional)"},
    )

    # -----------------------------------------------------------------
    #  Semana 13: clave foranea hacia la tabla proveedores.
    #  Las opciones NO se escriben aqui: se cargan desde la base de datos
    #  en la ruta, para que el desplegable refleje siempre los
    #  proveedores realmente registrados.
    #  coerce=int convierte el valor recibido (texto) al entero que
    #  espera la columna id_proveedor.
    # -----------------------------------------------------------------
    id_proveedor = SelectField(
        "Proveedor",
        validators=[Optional()],
        coerce=int,
        choices=[],
    )

    submit = SubmitField("Guardar producto")
