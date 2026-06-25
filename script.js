// =============================================
//   ELECTRIC LIFE – script.js
//   Semana 5 · Desarrollo de Aplicaciones Web
// =============================================

// ── Contador global de solicitudes ──────────────────────────────────────────
let totalRegistros = 0;

// ── Referencias al DOM ──────────────────────────────────────────────────────
const form            = document.getElementById('form-solicitud');
const inputNombre     = document.getElementById('sol-nombre');
const inputDesc       = document.getElementById('sol-descripcion');
const selectCategoria = document.getElementById('sol-categoria');
const listaRegistros  = document.getElementById('lista-registros');
const contadorEl      = document.getElementById('contador-registros');
const mensajeVacio    = document.getElementById('mensaje-vacio');

// ── Helpers de validación ────────────────────────────────────────────────────
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

// ── Validación en tiempo real ────────────────────────────────────────────────
[inputNombre, inputDesc, selectCategoria].forEach(el => {
  el.addEventListener('input', () => resetEstado(el));
});

// ── Actualizar contador en pantalla ─────────────────────────────────────────
function actualizarContador() {
  contadorEl.textContent = totalRegistros;
  mensajeVacio.style.display = totalRegistros === 0 ? 'block' : 'none';
}

// ── Mapa de ícono por categoría ──────────────────────────────────────────────
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

// ── Crear tarjeta de registro ─────────────────────────────────────────────────
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
          <button class="btn-eliminar btn btn-sm btn-outline-danger border-0 p-1 lh-1"
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

// ── Eliminar registro ────────────────────────────────────────────────────────
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
  }, 250);
}

// ── Toast de notificación ────────────────────────────────────────────────────
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

// ── Manejar submit del formulario ────────────────────────────────────────────
form.addEventListener('submit', (e) => {
  e.preventDefault(); // evitar recarga

  const nombre     = inputNombre.value.trim();
  const descripcion = inputDesc.value.trim();
  const categoria  = selectCategoria.value;

  let valido = true;

  // Validaciones
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

  if (!valido) return;

  // Crear y agregar tarjeta al DOM
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

  // Limpiar formulario
  form.reset();
  [inputNombre, inputDesc, selectCategoria].forEach(resetEstado);
  inputNombre.focus();
});

// ── Init ─────────────────────────────────────────────────────────────────────
actualizarContador();

// ── Active nav link on scroll ────────────────────────────────────────────────
const sections = document.querySelectorAll('section[id], header');
const navLinks  = document.querySelectorAll('.nav-link');

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