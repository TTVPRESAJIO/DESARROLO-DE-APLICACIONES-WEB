/* =====================================================================
   ELECTRIC LIFE IHC - electric-life.js
   ---------------------------------------------------------------------
   Continuacion del script de la Semana 8 (Desarrollo de Aplicaciones
   Web), adaptado a WordPress y ampliado con la capa de Interacción
   Humano - Computador.

   Cada bloque indica la heurística de Nielsen [Nx] y el criterio
   WCAG 2.1 que implementa.
===================================================================== */

(function () {
	'use strict';

	// Datos entregados por PHP mediante wp_localize_script.
	var SERVICIOS = (window.ELIHC && window.ELIHC.servicios) ? window.ELIHC.servicios : [];

	// -----------------------------------------------------------------
	// Utilidad: anuncia un texto a los lectores de pantalla.
	// [N1] Visibilidad del estado del sistema para usuarios ciegos.
	// WCAG 2.1: 4.1.3 Mensajes de estado.
	// -----------------------------------------------------------------
	function anunciar(texto) {
		var region = document.getElementById('ihc-anuncios');
		if (!region) return;
		region.textContent = '';
		window.setTimeout(function () {
			region.textContent = texto;
		}, 100);
	}

	// -----------------------------------------------------------------
	// Utilidad: notificacion emergente (toast).
	// [N1] Retroalimentacion inmediata y no bloqueante.
	// -----------------------------------------------------------------
	function toast(mensaje, tipo) {
		var cont = document.getElementById('toast-container');
		if (!cont) return;

		var colores = {
			exito: 'text-bg-success',
			error: 'text-bg-danger',
			info: 'text-bg-dark'
		};

		var el = document.createElement('div');
		el.className = 'toast align-items-center border-0 ' + (colores[tipo] || colores.info);
		el.setAttribute('role', 'alert');
		el.setAttribute('aria-live', 'assertive');
		el.setAttribute('aria-atomic', 'true');
		el.innerHTML =
			'<div class="d-flex">' +
			'<div class="toast-body">' + mensaje + '</div>' +
			'<button type="button" class="btn-close btn-close-white me-2 m-auto" ' +
			'data-bs-dismiss="toast" aria-label="Cerrar aviso"></button>' +
			'</div>';

		cont.appendChild(el);

		if (window.bootstrap && window.bootstrap.Toast) {
			var t = new window.bootstrap.Toast(el, { delay: 4500 });
			t.show();
			el.addEventListener('hidden.bs.toast', function () { el.remove(); });
		} else {
			window.setTimeout(function () { el.remove(); }, 4500);
		}
	}

	// =================================================================
	// 1. RENDERIZADO DE SERVICIOS (tarjetas + tabla)
	//    Un único arreglo alimenta las dos vistas: la información nunca
	//    se contradice entre formatos. [N4] Consistencia y estandares.
	// =================================================================
	function renderizarServicios() {
		var contenedor = document.getElementById('lista-servicios');
		var tbody = document.getElementById('tabla-servicios-body');
		var vacio = document.getElementById('servicios-vacio');
		var contenido = document.getElementById('servicios-contenido');

		if (!contenedor) return;

		contenedor.innerHTML = '';
		if (tbody) tbody.innerHTML = '';

		// Estado vacio: mensaje comprensible, no un error técnico. [N9]
		if (!SERVICIOS.length) {
			if (vacio) vacio.hidden = false;
			if (contenido) contenido.hidden = true;
			anunciar('No hay servicios disponibles en este momento.');
			return;
		}

		if (vacio) vacio.hidden = true;

		SERVICIOS.forEach(function (servicio, indice) {

			// ---- Tarjeta ----
			var col = document.createElement('div');
			col.className = 'col-sm-6 col-lg-3';
			col.innerHTML =
				'<article class="card service-card p-3 text-center h-100">' +
				'<div class="card-body d-flex flex-column">' +
				'<div class="card-icon"><i class="bi ' + servicio.icono + '" aria-hidden="true"></i></div>' +
				'<h3 class="card-title h6">' + servicio.titulo + '</h3>' +
				'<p class="card-text text-muted small flex-grow-1">' + servicio.texto + '</p>' +
				'<button type="button" class="btn btn-detalle btn-sm mt-2" data-index="' + indice + '" ' +
				'data-bs-toggle="modal" data-bs-target="#modalServicio">' +
				'<i class="bi bi-eye me-1" aria-hidden="true"></i>Ver detalles' +
				'<span class="screen-reader-text"> de ' + servicio.titulo + '</span>' +
				'</button>' +
				'</div>' +
				'</article>';
			contenedor.appendChild(col);

			// ---- Fila de la tabla ----
			if (tbody) {
				var tr = document.createElement('tr');
				tr.innerHTML =
					'<td class="text-center"><i class="bi ' + servicio.icono + ' icono-celda" aria-hidden="true"></i></td>' +
					'<th scope="row" class="fw-semibold">' + servicio.titulo + '</th>' +
					'<td class="text-muted small">' + servicio.texto + '</td>' +
					'<td class="text-center">' +
					'<button type="button" class="btn btn-detalle btn-sm" data-index="' + indice + '" ' +
					'data-bs-toggle="modal" data-bs-target="#modalServicio">' +
					'<i class="bi bi-eye" aria-hidden="true"></i>' +
					'<span class="screen-reader-text">Ver detalles de ' + servicio.titulo + '</span>' +
					'</button>' +
					'</td>';
				tbody.appendChild(tr);
			}
		});
	}

	// =================================================================
	// 2. CARGA CON SPINNER
	//    [N1] Visibilidad del estado: el sistema informa que esta
	//    trabajando en lugar de dejar la pantalla en blanco.
	// =================================================================
	function cargarServicios() {
		var spinner = document.getElementById('servicios-cargando');
		var contenido = document.getElementById('servicios-contenido');

		if (!spinner || !contenido) {
			renderizarServicios();
			return;
		}

		spinner.hidden = false;
		contenido.hidden = true;

		window.setTimeout(function () {
			renderizarServicios();
			spinner.hidden = true;
			if (SERVICIOS.length) {
				contenido.hidden = false;
				anunciar(SERVICIOS.length + ' servicios cargados correctamente.');
			}
		}, 700);
	}

	// =================================================================
	// 3. MODAL DE DETALLE
	//    [N2] Lenguaje del usuario  [N3] Salida clara y reversible.
	// =================================================================
	function prepararModal() {
		var modal = document.getElementById('modalServicio');
		if (!modal) return;

		modal.addEventListener('show.bs.modal', function (evento) {
			var boton = evento.relatedTarget;
			if (!boton) return;

			var servicio = SERVICIOS[parseInt(boton.getAttribute('data-index'), 10)];
			if (!servicio) return;

			modal.querySelector('#modal-titulo').textContent = servicio.titulo;
			modal.querySelector('#modal-texto').textContent = servicio.detalle;
			modal.querySelector('#modal-icono').className = 'bi ' + servicio.icono;

			// Se recuerda qué servicio se está viendo para poder trasladarlo
			// al formulario. [N6] Reconocer antes que recordar.
			var solicitar = modal.querySelector('#modal-solicitar');
			if (solicitar) {
				solicitar.setAttribute('data-index', boton.getAttribute('data-index'));
			}

			anunciar('Detalle de ' + servicio.titulo);
		});
	}

	// =================================================================
	//    PRECARGA DEL FORMULARIO DESDE EL MODAL
	//    Corrige el hallazgo de la evaluación heurística: el usuario
	//    tenía que volver a elegir en el formulario el servicio que ya
	//    había seleccionado al abrir el detalle.
	//    [N6] Reconocer antes que recordar  [N7] Eficiencia de uso.
	// =================================================================
	function prepararPrecarga() {
		var solicitar = document.getElementById('modal-solicitar');
		if (!solicitar) return;

		solicitar.addEventListener('click', function () {
			var servicio = SERVICIOS[parseInt(solicitar.getAttribute('data-index'), 10)];
			if (!servicio) return;

			var select = document.getElementById('sol-categoria');
			var texto = document.getElementById('sol-descripcion');
			var nombre = document.getElementById('sol-nombre');

			if (select && servicio.categoria) {
				select.value = servicio.categoria;
			}

			// Solo se propone el texto si el campo está vacío: nunca se
			// pisa lo que el usuario ya escribió. [N3] Control del usuario.
			if (texto && texto.value.trim() === '') {
				texto.value = 'Me interesa el servicio de ' + servicio.titulo + '. ';
				var evento = new Event('input', { bubbles: true });
				texto.dispatchEvent(evento);
			}

			window.setTimeout(function () {
				if (nombre) nombre.focus();
				toast('Preparamos el formulario para ' + servicio.titulo + '.', 'info');
				anunciar('Formulario preparado para el servicio ' + servicio.titulo +
					'. Solo falta tu nombre y los detalles.');
			}, 500);
		});
	}

	// =================================================================
	//    LIMPIAR FORMULARIO
	//    [N3] Control y libertad del usuario: salida clara a mitad de
	//    la tarea. Se pide confirmación porque la acción es destructiva
	//    y no tiene deshacer. [N5] Prevención de errores.
	// =================================================================
	function prepararLimpiar() {
		var boton = document.getElementById('btn-limpiar-solicitud');
		var form = document.getElementById('form-solicitud');
		if (!boton || !form) return;

		boton.addEventListener('click', function () {
			var hayContenido = Array.prototype.some.call(
				form.querySelectorAll('input[type=text], select, textarea'),
				function (campo) { return campo.value.trim() !== ''; }
			);

			if (!hayContenido) {
				toast('El formulario ya está vacío.', 'info');
				return;
			}

			if (!window.confirm('Se borrará todo lo que escribiste en el formulario. ¿Quieres continuar?')) {
				return;
			}

			form.reset();

			// Se retiran también los mensajes de error visibles.
			Array.prototype.forEach.call(form.querySelectorAll('.is-invalid'), function (campo) {
				limpiarError(campo);
			});

			// Se reinician los contadores de caracteres.
			Array.prototype.forEach.call(form.querySelectorAll('[data-contador]'), function (campo) {
				campo.dispatchEvent(new Event('input', { bubbles: true }));
			});

			var primero = document.getElementById('sol-nombre');
			if (primero) primero.focus();

			toast('Formulario vaciado.', 'info');
			anunciar('El formulario quedó vacío. El cursor está en el campo de nombre.');
		});
	}

	// =================================================================
	// 4. ALTERNADOR DE VISTA TARJETAS / TABLA
	//    [N7] Flexibilidad y eficiencia de uso: cada persona explora la
	//    información en el formato que le resulta más cómodo.
	//    aria-pressed comunica el estado del boton al lector de pantalla.
	// =================================================================
	function prepararVistas() {
		var btnTarjetas = document.getElementById('ver-tarjetas');
		var btnTabla = document.getElementById('ver-tabla');
		var lista = document.getElementById('lista-servicios');
		var tabla = document.getElementById('bloque-tabla');

		if (!btnTarjetas || !btnTabla || !lista || !tabla) return;

		function activar(vista) {
			var esTabla = (vista === 'tabla');
			tabla.hidden = !esTabla;
			lista.hidden = esTabla;
			btnTabla.setAttribute('aria-pressed', esTabla ? 'true' : 'false');
			btnTarjetas.setAttribute('aria-pressed', esTabla ? 'false' : 'true');
			anunciar(esTabla ? 'Vista de tabla comparativa activada.' : 'Vista de tarjetas activada.');
		}

		btnTarjetas.addEventListener('click', function () { activar('tarjetas'); });
		btnTabla.addEventListener('click', function () { activar('tabla'); });
	}

	// =================================================================
	// 5. VALIDACION DE FORMULARIOS EN EL NAVEGADOR
	//    Complementa (nunca sustituye) la validación del servidor.
	//    [N5] Prevencion de errores: se avisa antes de enviar.
	//    [N9] Recuperacion: el foco viaja al primer campo con problema.
	//    WCAG 2.1: 3.3.1 Identificacion de errores, 3.3.3 Sugerencias.
	// =================================================================
	function mensajePara(campo) {
		var v = campo.validity;
		var etiqueta = document.querySelector('label[for="' + campo.id + '"]');
		var nombre = etiqueta ? etiqueta.textContent.replace('*', '').trim() : 'Este campo';

		if (v.valueMissing) {
			return 'Falta completar "' + nombre + '".';
		}
		if (v.typeMismatch && campo.type === 'email') {
			return 'Ese correo no parece válido. Revisa que incluya @ y un dominio, por ejemplo: nombre@correo.com';
		}
		if (v.tooShort) {
			return 'Escribe al menos ' + campo.minLength + ' caracteres. Llevas ' + campo.value.length + '.';
		}
		if (v.tooLong) {
			return 'El maximo permitido es ' + campo.maxLength + ' caracteres.';
		}
		return 'Revisa el contenido de "' + nombre + '".';
	}

	function pintarError(campo, mensaje) {
		campo.classList.add('is-invalid');
		campo.setAttribute('aria-invalid', 'true');

		var id = campo.id + '-error';
		var caja = document.getElementById(id);

		if (!caja) {
			caja = document.createElement('span');
			caja.id = id;
			caja.className = 'invalid-feedback d-block';
			campo.parentNode.appendChild(caja);
		}

		caja.innerHTML = '<i class="bi bi-exclamation-circle-fill me-1" aria-hidden="true"></i>' + mensaje;
		campo.setAttribute('aria-describedby',
			((campo.getAttribute('aria-describedby') || '').replace(id, '').trim() + ' ' + id).trim());
	}

	function limpiarError(campo) {
		campo.classList.remove('is-invalid');
		campo.removeAttribute('aria-invalid');
		var caja = document.getElementById(campo.id + '-error');
		if (caja) caja.remove();
	}

	function prepararFormulario(form) {
		if (!form) return;

		var campos = form.querySelectorAll('input[required], select[required], textarea[required]');

		// Validación al salir del campo: el aviso llega temprano,
		// no al final del proceso. [N5]
		Array.prototype.forEach.call(campos, function (campo) {
			campo.addEventListener('blur', function () {
				if (campo.value.trim() === '') { limpiarError(campo); return; }
				if (!campo.checkValidity()) {
					pintarError(campo, mensajePara(campo));
				} else {
					limpiarError(campo);
				}
			});

			campo.addEventListener('input', function () {
				if (campo.classList.contains('is-invalid') && campo.checkValidity()) {
					limpiarError(campo);
				}
			});
		});

		form.addEventListener('submit', function (evento) {
			var primeroConError = null;

			Array.prototype.forEach.call(campos, function (campo) {
				if (!campo.checkValidity()) {
					pintarError(campo, mensajePara(campo));
					if (!primeroConError) primeroConError = campo;
				} else {
					limpiarError(campo);
				}
			});

			if (primeroConError) {
				evento.preventDefault();
				primeroConError.focus();
				toast('Revisa los campos marcados en rojo antes de enviar.', 'error');
				anunciar('El formulario tiene campos por corregir.');
				return;
			}

			// [N1] El boton confirma que la acción esta en curso y se
			// bloquea para evitar envios duplicados. [N5]
			var boton = form.querySelector('button[type="submit"]');
			if (boton) {
				boton.disabled = true;
				boton.innerHTML =
					'<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Enviando...';
			}
			anunciar('Enviando el formulario, espera un momento.');
		});
	}

	// =================================================================
	// 6. CONTADOR DE CARACTERES
	//    [N1] Estado visible  [Carga cognitiva] evita que el usuario
	//    tenga que estimar cuanto le queda de espacio.
	// =================================================================
	function prepararContadores() {
		var campos = document.querySelectorAll('[data-contador]');

		Array.prototype.forEach.call(campos, function (campo) {
			var salida = document.getElementById(campo.getAttribute('data-contador'));
			if (!salida) return;

			var maximo = parseInt(campo.getAttribute('maxlength'), 10) || 0;

			function actualizar() {
				var usados = campo.value.length;
				salida.textContent = usados + ' de ' + maximo + ' caracteres';
				salida.classList.remove('cerca-limite', 'en-limite');
				if (usados >= maximo) {
					salida.classList.add('en-limite');
				} else if (usados > maximo * 0.85) {
					salida.classList.add('cerca-limite');
				}
			}

			campo.addEventListener('input', actualizar);
			actualizar();
		});
	}

	// =================================================================
	//    VIDEO BAJO CONSENTIMIENTO
	//    El iframe de YouTube no existe en el HTML: se crea aqui, y solo
	//    cuando la persona lo pide o cuando ya habia aceptado las cookies
	//    de marketing.
	//    [N3] Control del usuario  [Etica] Decision informada.
	// =================================================================
	function prepararVideo() {
		var caja = document.getElementById('ihc-video');
		if (!caja) return;

		function cargar(reproducir) {
			var url = caja.getAttribute('data-video');
			if (!url) return;

			var marco = document.createElement('iframe');
			marco.src = url + (reproducir ? '?autoplay=1' : '');
			marco.title = 'Video informativo de Electric Life sobre sistemas solares de respaldo';
			marco.setAttribute('allowfullscreen', '');
			marco.setAttribute('allow', 'autoplay; encrypted-media');
			marco.setAttribute('loading', 'lazy');

			caja.innerHTML = '';
			caja.appendChild(marco);

			// El foco pasa al video para que quien navega con teclado no
			// se quede donde estaba un boton que ya no existe. [N1]
			marco.setAttribute('tabindex', '0');
			if (reproducir) { marco.focus(); }

			anunciar('Video cargado. El contenido también está disponible en texto más abajo.');
		}

		// Si ya habia consentimiento previo, se carga sin preguntar de nuevo.
		if (caja.getAttribute('data-consentido') === '1') {
			cargar(false);
			return;
		}

		var boton = document.getElementById('ihc-video-cargar');
		if (boton) {
			boton.addEventListener('click', function () { cargar(true); });
		}

		// Si la persona acepta las cookies mientras esta en la pagina,
		// el video aparece solo. Complianz emite este evento.
		document.addEventListener('cmplz_status_change', function (e) {
			if (e.detail && e.detail.category === 'marketing' && e.detail.value === 'allow') {
				cargar(false);
			}
		});
	}

	// =================================================================
	//    MAPA BAJO CONSENTIMIENTO
	//    Mismo criterio que el video: Google Maps instala cookies, asi
	//    que el iframe no existe hasta que la persona lo pide.
	// =================================================================
	function prepararMapa() {
		var caja = document.getElementById('ihc-mapa');
		if (!caja) return;

		function cargar() {
			var url = caja.getAttribute('data-mapa');
			if (!url) return;

			var marco = document.createElement('iframe');
			marco.src = url;
			marco.title = 'Mapa de ubicación de Electric Life en Puyo, Pastaza';
			marco.setAttribute('loading', 'lazy');
			marco.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
			marco.setAttribute('tabindex', '0');

			caja.innerHTML = '';
			caja.appendChild(marco);

			anunciar('Mapa cargado. La dirección también está escrita encima del mapa.');
		}

		if (caja.getAttribute('data-consentido') === '1') {
			cargar();
			return;
		}

		var boton = document.getElementById('ihc-mapa-cargar');
		if (boton) {
			boton.addEventListener('click', cargar);
		}

		document.addEventListener('cmplz_status_change', function (e) {
			if (e.detail && e.detail.category === 'marketing' && e.detail.value === 'allow') {
				cargar();
			}
		});
	}

	// =================================================================
	// 7. BARRA DE PROGRESO DE LECTURA
	//    [N1] Visibilidad del estado del sistema.
	// =================================================================
	function prepararProgreso() {
		var barra = document.getElementById('ihc-progreso');
		if (!barra) return;

		function actualizar() {
			var alto = document.documentElement.scrollHeight - window.innerHeight;
			var pct = alto > 0 ? Math.min(100, Math.round((window.scrollY / alto) * 100)) : 0;
			barra.style.width = pct + '%';
			barra.setAttribute('aria-valuenow', pct);
		}

		window.addEventListener('scroll', actualizar, { passive: true });
		window.addEventListener('resize', actualizar);
		actualizar();
	}

	// =================================================================
	// 8. BOTON VOLVER ARRIBA
	//    [N3] Control y libertad del usuario.
	// =================================================================
	function prepararBotonArriba() {
		var boton = document.getElementById('ihc-top');
		if (!boton) return;

		window.addEventListener('scroll', function () {
			boton.classList.toggle('visible', window.scrollY > 500);
		}, { passive: true });

		boton.addEventListener('click', function () {
			window.scrollTo({ top: 0, behavior: 'smooth' });
			var marca = document.querySelector('.navbar-brand');
			if (marca) marca.focus();
			anunciar('Volviste al inicio de la pagina.');
		});
	}

	// =================================================================
	// 9. RESALTADO DE LA SECCION ACTIVA EN EL MENU
	//    [N1] El usuario siempre sabe en que seccion esta.
	//    Se usa IntersectionObserver por eficiencia, con respaldo en
	//    scroll para navegadores antiguos. [Robusto]
	// =================================================================
	function prepararMenuActivo() {
		var secciones = document.querySelectorAll('main section[id]');
		var enlaces = document.querySelectorAll('#menu-principal .nav-link');

		if (!secciones.length || !enlaces.length || !('IntersectionObserver' in window)) return;

		function marcar(id) {
			Array.prototype.forEach.call(enlaces, function (enlace) {
				var destino = (enlace.getAttribute('href') || '').split('#')[1];
				var activo = (destino === id);
				enlace.classList.toggle('active', activo);
				if (activo) {
					enlace.setAttribute('aria-current', 'page');
				} else {
					enlace.removeAttribute('aria-current');
				}
			});
		}

		var observador = new IntersectionObserver(function (entradas) {
			entradas.forEach(function (entrada) {
				if (entrada.isIntersecting) marcar(entrada.target.id);
			});
		}, { rootMargin: '-40% 0px -55% 0px' });

		Array.prototype.forEach.call(secciones, function (seccion) {
			observador.observe(seccion);
		});
	}

	// =================================================================
	// 10. PREFERENCIAS DE ACCESIBILIDAD DEL USUARIO
	//     [N7] Flexibilidad y eficiencia de uso.
	//     La eleccion se conserva entre visitas, de modo que el usuario
	//     no tiene que repetirla. [Carga cognitiva]
	// =================================================================
	function prepararAccesibilidad() {
		var btnTexto = document.getElementById('ihc-btn-texto');
		var btnContraste = document.getElementById('ihc-btn-contraste');

		function alternar(boton, clase, clave, mensajeOn, mensajeOff) {
			if (!boton) return;

			var activo = false;
			try {
				activo = window.localStorage.getItem(clave) === '1';
			} catch (e) { activo = false; }

			function aplicar(estado) {
				document.body.classList.toggle(clase, estado);
				boton.setAttribute('aria-pressed', estado ? 'true' : 'false');
				try {
					window.localStorage.setItem(clave, estado ? '1' : '0');
				} catch (e) { /* almacenamiento no disponible */ }
			}

			aplicar(activo);

			boton.addEventListener('click', function () {
				var nuevo = boton.getAttribute('aria-pressed') !== 'true';
				aplicar(nuevo);
				anunciar(nuevo ? mensajeOn : mensajeOff);
				toast(nuevo ? mensajeOn : mensajeOff, 'info');
			});
		}

		alternar(btnTexto, 'ihc-texto-grande', 'elihc_texto',
			'Texto ampliado activado.', 'Texto ampliado desactivado.');

		alternar(btnContraste, 'ihc-alto-contraste', 'elihc_contraste',
			'Modo de alto contraste activado.', 'Modo de alto contraste desactivado.');
	}

	// =================================================================
	// 11. FOCO EN EL AVISO TRAS ENVIAR UN FORMULARIO
	//     [Norman etapas 5-6] Percepcion e interpretacion del resultado:
	//     el mensaje del sistema recibe el foco para que nadie se lo pierda.
	// =================================================================
	function enfocarAviso() {
		var aviso = document.querySelector('.ihc-aviso');
		if (!aviso) return;

		// Limpia el parametro de la URL para que al recargar no
		// reaparezca un mensaje viejo. [N5] Prevencion de errores.
		// El fragmento (#seccion) ya viene incluido en la URL, por lo que
		// no debe volver a concatenarse.
		if (window.history && window.history.replaceState) {
			var url = new URL(window.location.href);
			url.searchParams.delete('elihc_aviso');
			url.hash = aviso.id ? '#' + aviso.id : url.hash;
			window.history.replaceState({}, '', url.toString());
		}

		// Se lleva al usuario hasta el mensaje del sistema y se le da el
		// foco, para que ni la vista ni el lector de pantalla lo pasen por
		// alto. [Norman etapas 5-6] Percepcion e interpretacion.
		window.setTimeout(function () {
			aviso.scrollIntoView({ behavior: 'smooth', block: 'center' });
			aviso.focus({ preventScroll: true });
		}, 400);
	}

	// =================================================================
	// ARRANQUE
	// =================================================================
	document.addEventListener('DOMContentLoaded', function () {
		cargarServicios();
		prepararModal();
		prepararPrecarga();
		prepararLimpiar();
		prepararVistas();
		prepararFormulario(document.getElementById('form-solicitud'));
		prepararFormulario(document.getElementById('form-contacto'));
		prepararContadores();
		prepararVideo();
		prepararMapa();
		prepararProgreso();
		prepararBotonArriba();
		prepararMenuActivo();
		prepararAccesibilidad();
		enfocarAviso();
	});

})();
