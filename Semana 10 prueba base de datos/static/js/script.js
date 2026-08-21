// =====================================================================
//   ELECTRIC LIFE – script.js  (Semana 8)
//   Desarrollo de Aplicaciones Web
//
//   Semana 8 – Mejora de interfaces con Bootstrap:
//   Se CONSERVA toda la lógica de las semanas anteriores
//   (validaciones de la Semana 6 y renderizado dinámico de la
//   Semana 7) y se AÑADEN componentes de Bootstrap manejados desde
//   JavaScript:
//     • SPINNER  → carga simulada de los servicios.
//     • TABLA    → comparativa de servicios generada desde el arreglo.
//     • MODAL    → detalles de cada servicio.
//     • ALERTAS  → mensajes de éxito / error / aviso en Solicitudes.
//   La interfaz mejora; la lógica NO se elimina.
// =====================================================================


// =====================================================================
//   1. DATOS DEL PROYECTO (arreglo de objetos)
//      Se añade el campo "detalle" para mostrarlo en el MODAL (S8).
// =====================================================================
const servicios = [
  { icono: 'bi-box-seam-fill',                titulo: 'Venta de Sistemas Solares', texto: 'Kits completos de respaldo solar para todo tipo de consumo.',           detalle: 'Ofrecemos kits solares dimensionados según tu consumo: panel, inversor, batería de litio y accesorios. Incluye garantía y asesoría de instalación.' },
  { icono: 'bi-hammer',                       titulo: 'Instalación Profesional',   texto: 'Montaje de paneles solares con personal técnico certificado.',           detalle: 'Nuestro equipo certificado realiza el montaje, cableado y puesta en marcha del sistema, cumpliendo normas de seguridad eléctrica.' },
  { icono: 'bi-wifi',                         titulo: 'Internet sin Apagones',     texto: 'Mantén tu router activo durante cortes de luz con nuestros sistemas.',   detalle: 'Sistema de respaldo dedicado para tu router y ONT. Mantiene tu internet y teletrabajo activos hasta 8 horas durante un apagón.' },
  { icono: 'bi-lightbulb-fill',               titulo: 'Iluminación LED',           texto: 'Soluciones de iluminación de emergencia de bajo consumo.',               detalle: 'Focos y tiras LED de bajo consumo con activación automática ante cortes de energía. Ideales para hogar y negocio.' },
  { icono: 'bi-camera-video-fill',            titulo: 'Cámaras de Seguridad',      texto: 'Respaldo energético para tus cámaras de vigilancia 24/7.',               detalle: 'Respaldo energético para tu sistema de videovigilancia (DVR/NVR y cámaras), garantizando monitoreo continuo día y noche.' },
  { icono: 'bi-wrench-adjustable-circle-fill',titulo: 'Mantenimiento',             texto: 'Mantenimiento preventivo y correctivo para todos nuestros sistemas.',   detalle: 'Planes de mantenimiento preventivo y correctivo: limpieza de paneles, revisión de baterías y diagnóstico de rendimiento.' },
  { icono: 'bi-graph-up-arrow',               titulo: 'Optimización Energética',   texto: 'Evaluamos tu consumo y diseñamos la solución más eficiente.',            detalle: 'Analizamos tu consumo eléctrico y proponemos la configuración más eficiente para reducir costos y maximizar el respaldo.' },
  { icono: 'bi-chat-dots-fill',               titulo: 'Asesoría Personalizada',    texto: 'Te guiamos para elegir el sistema ideal según tu presupuesto.',          detalle: 'Asesoría gratuita para elegir el sistema ideal según tu presupuesto y necesidades. Sin compromiso.' },
];


// =====================================================================
//   2. RENDERIZADO DINÁMICO DE SERVICIOS (bucle + condición)
//      Semana 8: se muestran en CARDS y también en una TABLA Bootstrap,
//      ambas generadas desde el mismo arreglo.
// =====================================================================
function renderizarServicios() {
  const contenedor = document.getElementById('lista-servicios');
  const aviso      = document.getElementById('servicios-vacio');
  const tbody      = document.getElementById('tabla-servicios-body');
  if (!contenedor) return;

  contenedor.innerHTML = '';
  if (tbody) tbody.innerHTML = '';

  // ── CONDICIÓN: mostrar mensaje según el estado de los datos ──
  if (servicios.length === 0) {
    if (aviso) aviso.style.display = 'block';
    return;
  }
  if (aviso) aviso.style.display = 'none';

  // ── BUCLE: recorrer el arreglo y crear una tarjeta por servicio ──
  servicios.forEach((servicio, indice) => {
    // ---- Card (con botón que abre el MODAL de detalles) ----
    const col = document.createElement('div');
    col.className = 'col-sm-6 col-lg-3';
    col.innerHTML = `
      <div class="card service-card p-3 text-center">
        <div class="card-body d-flex flex-column">
          <div class="card-icon"><i class="bi ${servicio.icono}"></i></div>
          <h5 class="card-title">${servicio.titulo}</h5>
          <p class="card-text text-muted small flex-grow-1">${servicio.texto}</p>
          <button type="button" class="btn btn-detalle btn-sm mt-2"
                  data-index="${indice}"
                  data-bs-toggle="modal" data-bs-target="#modalServicio">
            <i class="bi bi-eye me-1"></i>Ver detalles
          </button>
        </div>
      </div>`;
    contenedor.appendChild(col);

    // ---- Fila de la TABLA Bootstrap ----
    if (tbody) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="text-center"><i class="bi ${servicio.icono} icono-celda"></i></td>
        <td class="fw-semibold">${servicio.titulo}</td>
        <td class="text-muted small">${servicio.texto}</td>
        <td class="text-center">
          <button type="button" class="btn btn-primary btn-sm"
                  data-index="${indice}"
                  data-bs-toggle="modal" data-bs-target="#modalServicio">
            <i class="bi bi-eye"></i>
          </button>
        </td>`;
      tbody.appendChild(tr);
    }
  });
}


// =====================================================================
//   3. SPINNER – carga simulada de los servicios (Semana 8)
//      Muestra un spinner de Bootstrap y, tras un breve proceso
//      simulado desde JS, renderiza las cards y la tabla.
// =====================================================================
function cargarServiciosConSpinner() {
  const spinner    = document.getElementById('servicios-cargando');
  const contenido  = document.getElementById('servicios-contenido');

  if (spinner) spinner.style.display = 'block';
  if (contenido) contenido.style.display = 'none';

  // Proceso simulado (p. ej. una consulta a servidor)
  setTimeout(() => {
    renderizarServicios();
    if (spinner) spinner.style.display = 'none';
    if (contenido) contenido.style.display = 'block';
  }, 900);
}


// =====================================================================
//   4. MODAL – detalles del servicio seleccionado (Semana 8)
// =====================================================================
function configurarModalServicio() {
  const modal = document.getElementById('modalServicio');
  if (!modal) return;

  // Bootstrap dispara este evento al abrir el modal; usamos el botón
  // que lo activó para saber qué servicio mostrar (data-index).
  modal.addEventListener('show.bs.modal', (event) => {
    const boton  = event.relatedTarget;
    if (!boton) return;
    const indice = Number(boton.getAttribute('data-index'));
    const s      = servicios[indice];
    if (!s) return;

    modal.querySelector('#modal-titulo').textContent = s.titulo;
    modal.querySelector('#modal-texto').textContent  = s.detalle;
    modal.querySelector('#modal-icono').className    = `bi ${s.icono}`;
  });
}


// =====================================================================
//   5. ALERTA BOOTSTRAP – mensajes de la sección Solicitudes (Semana 8)
//      tipo: 'success' | 'danger' | 'warning' | 'info'
// =====================================================================
let alertaTimeout = null;

function mostrarAlerta(mensaje, tipo = 'success') {
  const cont = document.getElementById('alerta-solicitud');
  if (!cont) return;

  const iconos = {
    success: 'bi-check-circle-fill',
    danger:  'bi-exclamation-triangle-fill',
    warning: 'bi-exclamation-circle-fill',
    info:    'bi-info-circle-fill',
  };

  cont.innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show d-flex align-items-center" role="alert">
      <i class="bi ${iconos[tipo] || iconos.info} me-2 fs-5"></i>
      <div>${mensaje}</div>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    </div>`;

  // Auto-ocultar la alerta después de unos segundos
  clearTimeout(alertaTimeout);
  alertaTimeout = setTimeout(() => {
    const alerta = cont.querySelector('.alert');
    if (alerta) alerta.classList.remove('show');
  }, 4000);
}


// =====================================================================
//   6. SOLICITUDES DINÁMICAS + VALIDACIONES (Semana 6, conservado)
// =====================================================================

// ── Contador global de solicitudes ──────────────────────────────────
let totalRegistros = 0;

// ── Referencias al DOM ──────────────────────────────────────────────
const form            = document.getElementById('form-solicitud');
const inputNombre     = document.getElementById('sol-nombre');
const inputDesc       = document.getElementById('sol-descripcion');
const selectCategoria = document.getElementById('sol-categoria');
const listaRegistros  = document.getElementById('lista-registros');
const contadorEl      = document.getElementById('contador-registros');
const mensajeVacio    = document.getElementById('mensaje-vacio');
const btnSubmit       = document.getElementById('btn-registrar');

// ── Semana 9: este script se carga en TODAS las paginas (base.html).
//    El formulario de solicitudes solo existe en la pagina principal,
//    por eso se comprueba antes de registrar sus eventos.
const haySolicitudes = form && inputNombre && inputDesc && selectCategoria
                    && listaRegistros && contadorEl && mensajeVacio && btnSubmit;

// ── Helpers de validación ───────────────────────────────────────────
function mostrarError(input, msg) {
  input.classList.add('is-invalid');
  const feedback = input.parentElement.querySelector('.invalid-feedback')
    || input.nextElementSibling;
  if (feedback) feedback.textContent = msg;
}

function limpiarError(input) {
  input.classList.remove('is-invalid');
  input.classList.add('is-valid');
}

function resetEstado(input) {
  input.classList.remove('is-invalid', 'is-valid');
}

// ── Validación en tiempo real ───────────────────────────────────────
if (haySolicitudes) {
  [inputNombre, inputDesc, selectCategoria].forEach(el => {
    el.addEventListener('input', () => resetEstado(el));
  });
}

// ── Actualizar contador en pantalla (CONDICIÓN sobre el estado) ─────
function actualizarContador() {
  if (!contadorEl || !mensajeVacio) return;
  contadorEl.textContent = totalRegistros;
  mensajeVacio.style.display = totalRegistros === 0 ? 'block' : 'none';
}

// ── Mapa de ícono por categoría ─────────────────────────────────────
const iconoCategoria = {
  'Sistema solar':        'bi-sun-fill',
  'Instalación':          'bi-hammer',
  'Internet sin apagones':'bi-wifi',
  'Iluminación LED':      'bi-lightbulb-fill',
  'Cámaras de seguridad': 'bi-camera-video-fill',
  'Mantenimiento':        'bi-wrench-adjustable-circle-fill',
  'Optimización':         'bi-graph-up-arrow',
  'Asesoría':             'bi-chat-dots-fill',
};

const colorCategoria = {
  'Sistema solar':        'success',
  'Instalación':          'warning',
  'Internet sin apagones':'info',
  'Iluminación LED':      'warning',
  'Cámaras de seguridad': 'danger',
  'Mantenimiento':        'secondary',
  'Optimización':         'primary',
  'Asesoría':             'success',
};

// ── Crear tarjeta de registro ───────────────────────────────────────
function crearTarjeta(nombre, descripcion, categoria) {
  totalRegistros++;

  const icono = iconoCategoria[categoria] || 'bi-lightning-charge-fill';
  const color = colorCategoria[categoria] || 'success';
  const id    = `registro-${totalRegistros}`;
  const fecha = new Date().toLocaleDateString('es-EC', {
    day: '2-digit', month: 'short', year: 'numeric',
  });

  // Contenedor col
  const col = document.createElement('div');
  col.className = 'col-sm-6 col-lg-4';
  col.id = id;

  // Card
  col.innerHTML = `
    <div class="card registro-card h-100 shadow-sm border-0 border-top border-4 border-${color}">
      <div class="card-body d-flex flex-column gap-2 p-3">

        <!-- Encabezado -->
        <div class="d-flex align-items-start justify-content-between gap-2">
          <div class="d-flex align-items-center gap-2">
            <div class="registro-icon bg-${color} bg-opacity-10 text-${color}">
              <i class="bi ${icono}"></i>
            </div>
            <span class="badge bg-${color} bg-opacity-75 text-white px-2 py-1" style="font-size:.7rem;">
              ${categoria}
            </span>
          </div>
          <button class="btn-eliminar btn btn-sm btn-danger border-0 p-1 lh-1"
                  data-id="${id}" title="Eliminar registro"
                  aria-label="Eliminar registro de ${nombre}">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Nombre -->
        <h6 class="fw-bold mb-0 text-dark" style="font-family:'Poppins',sans-serif;">${nombre}</h6>

        <!-- Descripción -->
        <p class="text-muted small mb-0 flex-grow-1">${descripcion}</p>

        <!-- Footer fecha + número -->
        <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
          <small class="text-muted"><i class="bi bi-calendar3 me-1"></i>${fecha}</small>
          <small class="text-muted fw-semibold">#${totalRegistros}</small>
        </div>
      </div>
    </div>`;

  // Evento eliminar usando addEventListener
  col.querySelector('.btn-eliminar').addEventListener('click', () => {
    eliminarRegistro(id);
  });

  return col;
}

// ── Eliminar registro ───────────────────────────────────────────────
function eliminarRegistro(id) {
  const el = document.getElementById(id);
  if (!el) return;

  // Animación de salida
  el.style.transition = 'opacity .25s, transform .25s';
  el.style.opacity    = '0';
  el.style.transform  = 'scale(.95)';

  setTimeout(() => {
    el.remove();
    totalRegistros--;
    actualizarContador();
    mostrarToast('Registro eliminado.', 'warning');
    mostrarAlerta('Se eliminó una solicitud del listado.', 'warning');
  }, 250);
}

// ── Toast de notificación ───────────────────────────────────────────
function mostrarToast(mensaje, tipo = 'success') {
  const contenedor = document.getElementById('toast-container');

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${tipo} border-0 show`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body fw-semibold">${mensaje}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto"
              data-bs-dismiss="toast"></button>
    </div>`;

  contenedor.appendChild(toast);

  // Auto-cierre
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ── Registrar la solicitud (crea la tarjeta y notifica) ─────────────
function registrarSolicitud(nombre, descripcion, categoria) {
  const tarjeta = crearTarjeta(nombre, descripcion, categoria);

  // Insertar con animación
  tarjeta.style.opacity   = '0';
  tarjeta.style.transform = 'translateY(16px)';
  listaRegistros.appendChild(tarjeta); // appendChild

  requestAnimationFrame(() => {
    tarjeta.style.transition = 'opacity .3s, transform .3s';
    tarjeta.style.opacity    = '1';
    tarjeta.style.transform  = 'translateY(0)';
  });

  actualizarContador();
  mostrarToast(`✔ Solicitud de <strong>${nombre}</strong> registrada.`);
  mostrarAlerta(`Solicitud de <strong>${nombre}</strong> registrada correctamente.`, 'success');

  // Limpiar formulario
  form.reset();
  [inputNombre, inputDesc, selectCategoria].forEach(resetEstado);
  inputNombre.focus();
}

// ── Manejar submit del formulario (validaciones + registro) ─────────
if (haySolicitudes) form.addEventListener('submit', (e) => {
  e.preventDefault(); // evitar recarga

  const nombre      = inputNombre.value.trim();
  const descripcion = inputDesc.value.trim();
  const categoria   = selectCategoria.value;

  let valido = true;

  // Validaciones dinámicas (conservadas de la Semana 6)
  if (!nombre) {
    mostrarError(inputNombre, 'El nombre no puede estar vacío.');
    valido = false;
  } else if (nombre.length < 3) {
    mostrarError(inputNombre, 'Mínimo 3 caracteres.');
    valido = false;
  } else {
    limpiarError(inputNombre);
  }

  if (!descripcion) {
    mostrarError(inputDesc, 'Por favor describe tu solicitud.');
    valido = false;
  } else if (descripcion.length < 10) {
    mostrarError(inputDesc, 'Mínimo 10 caracteres.');
    valido = false;
  } else {
    limpiarError(inputDesc);
  }

  if (!categoria) {
    mostrarError(selectCategoria, 'Elige una categoría.');
    valido = false;
  } else {
    limpiarError(selectCategoria);
  }

  // ── CONDICIÓN: si algo falla, ALERTA de error y no se registra ──
  if (!valido) {
    mostrarAlerta('Revisa el formulario: hay campos con errores.', 'danger');
    return;
  }

  // ── SPINNER en el botón: proceso simulado antes de registrar ──
  const htmlOriginal = btnSubmit.innerHTML;
  btnSubmit.disabled = true;
  btnSubmit.innerHTML =
    '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Procesando…';

  setTimeout(() => {
    btnSubmit.disabled  = false;
    btnSubmit.innerHTML = htmlOriginal;
    registrarSolicitud(nombre, descripcion, categoria);
  }, 700);
});


// =====================================================================
//   7. INICIALIZACIÓN
// =====================================================================
cargarServiciosConSpinner();  // spinner + render de servicios (cards + tabla)
configurarModalServicio();    // prepara el modal de detalles
actualizarContador();         // estado inicial del contador / mensaje vacío


// =====================================================================
//   8. Active nav link on scroll (resaltar menú activo)
// =====================================================================
const sections = document.querySelectorAll('section[id], header');

// Semana 9: solo se resaltan los enlaces internos (#seccion).
// Los enlaces de las rutas Flask (/productos, /clientes, …) mantienen
// la clase "active" que asigna Jinja2 en base.html.
const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

if (navLinks.length > 0) {
  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 100) {
        current = sec.getAttribute('id') || 'inicio';
      }
    });
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  });
}

// ---------------------------------------------------------------
// Semana 10: confirmacion de carga del contenido dinamico Jinja2
// ---------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  console.log("Electric Life - contenido dinamico cargado con Jinja2");
});
