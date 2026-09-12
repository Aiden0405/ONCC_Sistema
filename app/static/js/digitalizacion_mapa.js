const estadoCambios = { creados: [], actualizados: {}, eliminados: new Set(), comunidad: null, layout: null };
const mapaCapas = {};
let capaComunidad = null; 
let capaLayout = null;
let geometriaComunidadOriginal = null;
let catalogoSimbolos = [];
const historialAcciones = [];
const ZOOM_BASE_ESCALA = 16;
let posicionOriginalLayout = null; 

// --- FUNCIONES DE APOYO ---
function parsearEstilo(estilo) {
    if (!estilo) return {};
    if (typeof estilo === 'string') { try { return JSON.parse(estilo); } catch (e) { return {}; } }
    return estilo;
}

function obtenerEstiloVisual(props) {
    const estPers = parsearEstilo(props.estilo_personalizado);
    const estDef = parsearEstilo(props.estilo_defecto);
    return Object.assign({}, estDef, estPers);
}

function asegurarPatronSVG(tipo, color) {
    if (!tipo || tipo === 'solido') return color;
    const idPatron = `patron-${tipo}-${color.replace('#', '')}`;
    let defs = document.getElementById('mapa-patrones-defs');
    
    if (!defs) {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.style.position = "absolute";
        defs = document.createElementNS("http://www.w3.org/2000/svg", "defs"); defs.id = 'mapa-patrones-defs';
        svg.appendChild(defs); document.body.appendChild(svg);
    }

    if (!document.getElementById(idPatron)) {
        const pattern = document.createElementNS("http://www.w3.org/2000/svg", "pattern");
        pattern.setAttribute("id", idPatron); pattern.setAttribute("patternUnits", "userSpaceOnUse");
        pattern.setAttribute("width", "12"); pattern.setAttribute("height", "12");

        let innerHTML = ''; let baseTransform = '';
        if (tipo === 'rayado') { baseTransform = "rotate(45)"; innerHTML = `<line x1="0" y1="-2" x2="0" y2="14" stroke="${color}" stroke-width="4" />`; } 
        else if (tipo === 'cuadricula') { innerHTML = `<rect width="12" height="12" fill="none" stroke="${color}" stroke-width="2" />`; } 
        else if (tipo === 'triangulo') { innerHTML = `<polygon points="6,0 12,12 0,12" fill="${color}" fill-opacity="0.7"/>`; } 
        else if (tipo === 'pentagono') { innerHTML = `<polygon points="6,0 12,4 10,12 2,12 0,4" fill="${color}" fill-opacity="0.7"/>`; }
        
        const currentZoom = window.map ? window.map.getZoom() : ZOOM_BASE_ESCALA;
        const initScale = Math.max(0.2, Math.pow(2, currentZoom - ZOOM_BASE_ESCALA));
        pattern.setAttribute("data-basetransform", baseTransform); pattern.setAttribute("patternTransform", `${baseTransform} scale(${initScale})`);
        pattern.innerHTML = innerHTML; defs.appendChild(pattern);
    }
    return `url(#${idPatron})`;
}

function escalarEstilosPorZoom() {
    if (!window.map) return;
    const scale = Math.max(0.1, Math.min(Math.pow(2, window.map.getZoom() - ZOOM_BASE_ESCALA), 10));
    const defs = document.getElementById('mapa-patrones-defs');
    if (defs) { defs.querySelectorAll('pattern').forEach(p => { p.setAttribute('patternTransform', `${p.getAttribute('data-basetransform') || ''} scale(${scale})`); }); }

    Object.values(mapaCapas).forEach(capa => {
        if (capa.setStyle && capa.feature) {
            const est = obtenerEstiloVisual(capa.feature.properties);
            const isLine = capa instanceof L.Polyline && !(capa instanceof L.Polygon);
            capa.setStyle({ weight: Math.max(0.5, Math.min((est.weight !== undefined ? est.weight : (isLine ? 4 : 2)) * scale, 25)), dashArray: est.dashArray ? est.dashArray.split(',').map(n => Math.max(1, parseFloat(n.trim()) * scale)).join(', ') : null });
        }
    });
}

window.aplicarEstilosSwalUI = function(btn) {
    const popup = Swal.getPopup();
    if (!popup) return;

    const inputActivo = popup.querySelector('#swal-personalizacion-activa');
    if (inputActivo) {
        inputActivo.value = '1';
    }
    
    // Dar feedback visual sin destruir el modal de SweetAlert2
    if (btn) {
        const textoOriginal = btn.innerHTML;
        btn.innerHTML = '¡Aplicado! ✓';
        btn.classList.replace('bg-blue-600', 'bg-green-600');
        btn.classList.replace('hover:bg-blue-700', 'hover:bg-green-700');
        
        setTimeout(() => {
            btn.innerHTML = textoOriginal;
            btn.classList.replace('bg-green-600', 'bg-blue-600');
            btn.classList.replace('hover:bg-green-700', 'hover:bg-blue-700');
        }, 2000);
    }
};

window.limpiarEstilosSwal = function(btn) {
    const popup = Swal.getPopup();
    if (!popup) return;

    const inputActivo = popup.querySelector('#swal-personalizacion-activa');
    if (inputActivo) inputActivo.value = '0';

    const colorInput = popup.querySelector('#swal-color-personalizado');
    if (colorInput) colorInput.value = '#3388ff';

    const patronInput = popup.querySelector('#swal-patron');
    if (patronInput) patronInput.value = 'solido';

    const grosorEl = popup.querySelector('#swal-grosor');
    if (grosorEl) grosorEl.value = '2';

    const bordeInput = popup.querySelector('#swal-borde-estilo');
    if (bordeInput) bordeInput.value = '';

    window.quitarIconoSwal();
    
    const validMsg = popup.querySelector('.swal2-validation-message');
    if (validMsg) validMsg.remove(); 
    
    // Dar feedback visual sin destruir el modal
    if (btn) {
        const textoOriginal = btn.innerHTML;
        btn.innerHTML = '¡Removido! ✗';
        setTimeout(() => {
            btn.innerHTML = textoOriginal;
        }, 2000);
    }
};

window.quitarIconoSwal = function() {
    const popup = Swal.getPopup();
    if (!popup) return;
    
    const iconB64 = popup.querySelector('#swal-icono-b64');
    const iconFile = popup.querySelector('#swal-icono-file');
    const prev = popup.querySelector('#preview-icono');
    const container = popup.querySelector('#preview-icono-container');
    
    if (iconB64) iconB64.value = '';
    if (iconFile) iconFile.value = '';
    if (prev) prev.src = '';
    if (container) container.style.display = 'none';
};

function recolectarEstilosSwal() {
    const popup = Swal.getPopup();
    if (!popup) return null; // Garantizar que leemos del modal activo

    const inputActivo = popup.querySelector('#swal-personalizacion-activa');
    // Validar explícitamente si se activó el botón
    if (!inputActivo || inputActivo.value !== '1') {
        return null;
    }

    const colorInput = popup.querySelector('#swal-color-personalizado')?.value || '#3388ff';
    const patronInput = popup.querySelector('#swal-patron')?.value || 'solido';
    const grosorEl = popup.querySelector('#swal-grosor');
    const grosorInput = grosorEl ? (parseInt(grosorEl.value) || 0) : 2;
    const bordeInput = popup.querySelector('#swal-borde-estilo')?.value || '';
    const iconInput = popup.querySelector('#swal-icono-b64')?.value || ''; 

    let estilo = {};
    if (iconInput && iconInput.trim() !== '') { 
        estilo.isIcon = true; 
        estilo.iconUrl = iconInput; 
        estilo.iconSize = [30, 30]; 
    } else {
        estilo.isIcon = false; 
        estilo.color = colorInput; 
        estilo.fillColor = colorInput; 
        if (popup.querySelector('#swal-patron')) estilo.patron = patronInput;
        if (grosorEl) estilo.weight = grosorInput;
        if (popup.querySelector('#swal-borde-estilo')) estilo.dashArray = bordeInput || null;
        estilo.fillOpacity = 0.8; 
        estilo.radius = 7;
    }
    return estilo;
}

function obtenerHtmlFormularioElemento(opcionesSimbologia, tipoFigura, datosPrevios = null) {
    const est = datosPrevios ? datosPrevios.estilo_personalizado || {} : {};
    const isComunidad = datosPrevios ? datosPrevios.modo === 'comunidad' : false;
    const nombrePropioActual = datosPrevios ? (datosPrevios.nombre_propio || '') : '';
    const esPoligono = (tipoFigura === 'Polygon' || tipoFigura === 'Rectangle');
    const esPunto = (tipoFigura === 'Marker' || tipoFigura === 'Point' || tipoFigura === 'CircleMarker');
    const tienePersonalizacionActiva = datosPrevios && datosPrevios.estilo_personalizado && Object.keys(datosPrevios.estilo_personalizado).length > 0;

    let html = `<div class="space-y-4 text-left">`;
    
    if (!datosPrevios) {
        html += `
        <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase">¿Qué estás dibujando?</label>
            <select id="swal-modo" class="w-full mt-1 p-2 border rounded-md text-sm bg-gray-50 outline-none" onchange="document.getElementById('div-elemento').style.display = this.value === 'comunidad' ? 'none' : 'block'">
                <option value="elemento" selected>Elemento Interno (Riesgo, Vía, Recurso...)</option>`;
        if (esPoligono) {
            html += `<option value="comunidad">Poligonal de la Comunidad (Límite)</option>`;
        }
        html += `</select>
        </div>`;
    }
    
    const tieneIcono = est.isIcon && est.iconUrl;

    html += `
        <!-- Input oculto para controlar si se activa o no el estilo personalizado -->
        <input type="hidden" id="swal-personalizacion-activa" value="${tienePersonalizacionActiva ? '1' : '0'}">

        <div id="div-elemento" class="space-y-4" ${isComunidad ? 'style="display: none;"' : ''}>
            <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Simbología</label>
                <select id="swal-simbologia" class="w-full mt-1 p-2 border border-gray-300 rounded-md text-sm outline-none bg-gray-50">${opcionesSimbologia}</select>
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Nombre Propio (Opcional)</label>
                <input type="text" id="swal-nombre-propio" value="${nombrePropioActual}" placeholder="Ej: Quebrada La Ruezga" class="w-full mt-1 p-2 border border-gray-300 rounded-md text-sm outline-none shadow-sm">
            </div>
            <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg shadow-sm relative">
                <div class="flex flex-wrap justify-between items-center mb-2 gap-1">
                    <label class="block text-xs font-semibold text-blue-800 uppercase">Personalización (${esPunto ? 'Marcador' : (esPoligono ? 'Polígono' : 'Línea')})</label>
                    <div class="flex items-center gap-1">
                        <!-- NOTA: Se ha agregado "this" a las llamadas onclick -->
                        <button type="button" onclick="aplicarEstilosSwalUI(this)" class="text-[10px] bg-blue-600 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded shadow-sm transition">Aplicar Personalizado</button>
                        <button type="button" onclick="limpiarEstilosSwal(this)" class="text-[10px] bg-red-100 hover:bg-red-200 text-red-700 font-bold py-1 px-2 rounded border border-red-200 transition">Quitar Estilo</button>
                    </div>
                </div>`;

    if (esPunto) {
        html += `
            <div class="grid grid-cols-1 gap-3 mt-2">
                <div>
                    <label class="text-xs text-gray-700 font-medium">Icono Personalizado</label>
                    <input type="file" id="swal-icono-file" accept="image/png, image/jpeg, image/svg+xml, image/webp" class="w-full p-1.5 border border-gray-300 rounded text-xs outline-none shadow-sm bg-white" onchange="if(this.files[0]){ const r = new FileReader(); r.onload=e=>{ document.getElementById('swal-icono-b64').value=e.target.result; const p = document.getElementById('preview-icono'); p.src=e.target.result; document.getElementById('preview-icono-container').style.display='flex'; }; r.readAsDataURL(this.files[0]); }">
                    <input type="hidden" id="swal-icono-b64" value="${est.iconUrl || ''}">
                </div>

                <!-- Recuadro debajo de subir icono con el icono actual en tiempo real -->
                <div id="preview-icono-container" class="p-2 bg-white border border-gray-200 rounded-md flex items-center gap-3 shadow-sm" style="${tieneIcono ? 'display: flex;' : 'display: none;'}">
                    <span class="text-[11px] font-medium text-gray-600">Icono actual:</span>
                    <img id="preview-icono" src="${est.iconUrl || ''}" class="h-10 w-10 object-contain bg-gray-50 border border-gray-200 rounded p-1 shadow-sm" alt="Vista previa">
                    <button type="button" onclick="quitarIconoSwal()" class="ml-auto text-xs bg-red-50 hover:bg-red-100 text-red-600 font-semibold px-2 py-1 rounded border border-red-200 transition">Quitar icono</button>
                </div>

                <div>
                    <label class="text-xs text-gray-700 font-medium">Color Base (aplica si no hay ícono)</label>
                    <input type="color" id="swal-color-personalizado" value="${est.color || '#3388ff'}" class="w-full h-8 rounded cursor-pointer border border-gray-300 p-0 shadow-sm">
                </div>
            </div>`;
    } else {
        html += `
            <div class="grid grid-cols-2 gap-3 mt-2">
                <div>
                    <label class="text-xs text-gray-700 font-medium">Color Base</label>
                    <input type="color" id="swal-color-personalizado" value="${est.color || '#3388ff'}" class="w-full h-8 rounded cursor-pointer border border-gray-300 p-0 shadow-sm">
                </div>`;

        if (esPoligono) {
            html += `
                <div>
                    <label class="text-xs text-gray-700 font-medium">Patrón</label>
                    <select id="swal-patron" class="w-full p-1.5 border border-gray-300 rounded text-xs outline-none shadow-sm bg-white">
                        <option value="solido" ${est.patron === 'solido' ? 'selected' : ''}>Color Sólido</option>
                        <option value="rayado" ${est.patron === 'rayado' ? 'selected' : ''}>Rayado</option>
                        <option value="cuadricula" ${est.patron === 'cuadricula' ? 'selected' : ''}>Cuadrícula</option>
                        <option value="triangulo" ${est.patron === 'triangulo' ? 'selected' : ''}>Triángulos</option>
                        <option value="pentagono" ${est.patron === 'pentagono' ? 'selected' : ''}>Pentágonos</option>
                    </select>
                </div>`;
        }

        html += `
                <div>
                    <label class="text-xs text-gray-700 font-medium">Grosor Borde</label>
                    <input type="number" id="swal-grosor" value="${est.weight !== undefined ? est.weight : 2}" min="0" max="10" class="w-full p-1.5 border border-gray-300 rounded text-xs outline-none shadow-sm bg-white">
                </div>
                <div>
                    <label class="text-xs text-gray-700 font-medium">Estilo de Borde</label>
                    <select id="swal-borde-estilo" class="w-full p-1.5 border border-gray-300 rounded text-xs outline-none shadow-sm bg-white">
                        <option value="" ${!est.dashArray ? 'selected' : ''}>Continuo</option>
                        <option value="5,5" ${est.dashArray === '5,5' ? 'selected' : ''}>Punteado</option>
                        <option value="15,10" ${est.dashArray === '15,10' ? 'selected' : ''}>Discontinuo</option>
                    </select>
                </div>
            </div>`;
    }

    html += `
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Descripción (Opcional)</label>
                <textarea id="swal-desc" rows="3" class="w-full mt-1 p-2 border border-gray-300 rounded-md text-sm outline-none shadow-sm">${datosPrevios ? (datosPrevios.descripcion || '') : ''}</textarea>
            </div>
        </div>
    </div>`;
    
    return html;
}

function validarFormularioSwal() {
    const grosorEl = document.getElementById('swal-grosor');
    if (grosorEl) {
        const grosor = parseInt(grosorEl.value) || 0;
        if (grosor > 10) { Swal.showValidationMessage('El grosor no puede ser mayor a 10.'); return false; }
    }
    return true;
}

// --- MANEJO DE HISTORIAL ---
function actualizarBotonDeshacer() {
    const btn = document.getElementById('btn-deshacer');
    if (historialAcciones.length > 0) { btn.removeAttribute('disabled'); btn.classList.remove('opacity-50', 'cursor-not-allowed'); } 
    else { btn.setAttribute('disabled', 'true'); btn.classList.add('opacity-50', 'cursor-not-allowed'); }
}

function deshacerUltimaAccion() {
    if (historialAcciones.length === 0) return;

    const ultimaAccion = historialAcciones.pop();

    if (ultimaAccion.tipo === 'editar_elemento') {
        const fid = ultimaAccion.id;
        let capa = ultimaAccion.capa || mapaCapas[fid];
        if (!capa) return;

        capa.feature.properties = JSON.parse(JSON.stringify(ultimaAccion.propsAnteriores));
        const props = capa.feature.properties;

        capa.id_simbologia = props.id_simbologia;
        capa.nombre_elemento = props.nombre_elemento;
        capa.nombre_propio = props.nombre_propio;
        capa.descripcion = props.descripcion;
        capa.estiloCustom = props.estilo_personalizado;

        if (ultimaAccion.actualizacionAnterior) {
            estadoCambios.actualizados[fid] = JSON.parse(JSON.stringify(ultimaAccion.actualizacionAnterior));
        } else {
            delete estadoCambios.actualizados[fid];
        }

        const estVisual = obtenerEstiloVisual(props);
        const esPuntoCapa = capa instanceof L.Marker || capa instanceof L.CircleMarker;

        if (esPuntoCapa) {
            const latlng = capa.getLatLng();
            if (estVisual.isIcon && estVisual.iconUrl) {
                if (capa instanceof L.CircleMarker) {
                    map.removeLayer(capa);
                    const newMarker = L.marker(latlng, {
                        icon: L.icon({ iconUrl: estVisual.iconUrl, iconSize: estVisual.iconSize || [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -15] })
                    });
                    newMarker.feature = capa.feature; newMarker.featureId = fid; newMarker.id_elemento = capa.id_elemento;
                    newMarker.id_simbologia = capa.id_simbologia; newMarker.nombre_elemento = capa.nombre_elemento;
                    newMarker.nombre_propio = capa.nombre_propio; newMarker.descripcion = capa.descripcion; newMarker.estiloCustom = capa.estiloCustom;
                    newMarker.on('click', function(e) { abrirPopupUnico(newMarker, props, fid, e.latlng); });
                    newMarker.addTo(map); mapaCapas[fid] = newMarker; capa = newMarker;
                } else if (capa instanceof L.Marker) {
                    capa.setIcon(L.icon({ iconUrl: estVisual.iconUrl, iconSize: estVisual.iconSize || [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -15] }));
                }
            } else {
                if (capa instanceof L.Marker) {
                    map.removeLayer(capa);
                    const newCircle = L.circleMarker(latlng, {
                        radius: estVisual.radius || 7,
                        color: estVisual.color || '#3388ff',
                        fillColor: estVisual.fillColor || estVisual.color || '#3388ff',
                        fillOpacity: estVisual.fillOpacity !== undefined ? estVisual.fillOpacity : 0.8,
                        weight: estVisual.weight !== undefined ? estVisual.weight : 2
                    });
                    newCircle.feature = capa.feature; newCircle.featureId = fid; newCircle.id_elemento = capa.id_elemento;
                    newCircle.id_simbologia = capa.id_simbologia; newCircle.nombre_elemento = capa.nombre_elemento;
                    newCircle.nombre_propio = capa.nombre_propio; newCircle.descripcion = capa.descripcion; newCircle.estiloCustom = capa.estiloCustom;
                    newCircle.on('click', function(e) { abrirPopupUnico(newCircle, props, fid, e.latlng); });
                    newCircle.addTo(map); mapaCapas[fid] = newCircle; capa = newCircle;
                } else if (capa instanceof L.CircleMarker) {
                    capa.setStyle({
                        radius: estVisual.radius || 7,
                        color: estVisual.color || '#3388ff',
                        fillColor: estVisual.fillColor || estVisual.color || '#3388ff',
                        fillOpacity: estVisual.fillOpacity !== undefined ? estVisual.fillOpacity : 0.8,
                        weight: estVisual.weight !== undefined ? estVisual.weight : 2
                    });
                }
            }
        } else if (typeof capa.setStyle === 'function') {
            capa.setStyle({
                color: estVisual.color || '#3388ff',
                fillColor: asegurarPatronSVG(estVisual.patron, estVisual.color || '#3388ff'),
                weight: estVisual.weight !== undefined ? estVisual.weight : 2,
                dashArray: estVisual.dashArray || null,
                fillOpacity: 0.8
            });
        }

        actualizarPopup(capa, props, fid);
        
        if (capa.getPopup()) {
            const nuevoContenido = typeof generarContenidoPopup === 'function' 
                ? generarContenidoPopup(capa, props, fid) 
                : `<b>${props.nombre_propio || props.nombre_elemento}</b><br>${props.descripcion || ''}`;
            
            capa.setPopupContent(nuevoContenido);
        }

        renderizarLeyenda();
        escalarEstilosPorZoom();
        actualizarBotonDeshacer();
    }
}

function hayCambiosPendientes() { 
    return estadoCambios.creados.length > 0 || Object.keys(estadoCambios.actualizados).length > 0 || estadoCambios.eliminados.size > 0 || estadoCambios.comunidad !== null || estadoCambios.layout !== null; 
}

// --- LOGICA DEL LAYOUT ---
function isLayerInsideLayout(layer, layoutLayer) {
    if (!layoutLayer) return false;
    const boundsLayout = layoutLayer.getBounds();
    if (typeof layer.eachLayer === 'function') {
        let inside = true;
        layer.eachLayer(l => { 
            if (l.getBounds && !boundsLayout.contains(l.getBounds())) inside = false; 
            else if (l.getLatLng && !boundsLayout.contains(l.getBounds())) inside = false; 
        });
        return inside;
    }
    if (layer.getBounds) { return boundsLayout.contains(layer.getBounds()); } 
    else if (layer.getLatLng) { return boundsLayout.contains(layer.getLatLng()); }
    return false;
}

async function validarYLimpiarFueraDeLayout(accion = 'mover') {
    if (!capaLayout) return true;
    let elementosFuera = [];

    Object.values(mapaCapas).forEach(el => {
        if (!isLayerInsideLayout(el, capaLayout)) elementosFuera.push(el);
    });

    if (capaComunidad && !isLayerInsideLayout(capaComunidad, capaLayout)) {
        elementosFuera.push(capaComunidad);
    }

    if (elementosFuera.length > 0) {
        const result = await Swal.fire({
            title: 'Elementos quedarán fuera',
            text: `Al ${accion} el marco, ${elementosFuera.length} elemento(s) quedarán por fuera y serán borrados. ¿Estás seguro?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar'
        });

        if (!result.isConfirmed) {
            if (posicionOriginalLayout) capaLayout.setBounds(posicionOriginalLayout);
            return false; 
        }

        for (let el of elementosFuera) {
            if (el === capaComunidad) {
                map.removeLayer(capaComunidad); 
                capaComunidad = null; 
                estadoCambios.comunidad = "ELIMINAR";
            } else {
                let fid = String(el.featureId);
                if (fid.startsWith('temp_')) { 
                    estadoCambios.creados = estadoCambios.creados.filter(c => c.tempId !== fid); 
                } else { 
                    estadoCambios.eliminados.add(fid); 
                    delete estadoCambios.actualizados[fid]; 
                }
                map.removeLayer(el); 
                delete mapaCapas[fid];
            }
        }
        if (typeof renderizarLeyenda === 'function') renderizarLeyenda();
    }
    posicionOriginalLayout = capaLayout.getBounds();
    if (typeof estadoCambios !== 'undefined') estadoCambios.layout = capaLayout.getBounds(); 
    return true;
}

function insertarLayoutEnMapa(limitesCalculados) {
capaLayout = L.rectangle(limitesCalculados, { 
    color: '#dc2626', 
    weight: 3, 
    fillOpacity: 0.05, 
    dashArray: '8, 8', 
    interactive: true 
}).addTo(map);

capaLayout.isLayout = true;
posicionOriginalLayout = capaLayout.getBounds();
if (typeof estadoCambios !== 'undefined') estadoCambios.layout = capaLayout.getBounds(); 

capaLayout.options.pmIgnore = false; 
map.pm.addControls({ drawRectangle: true, drawPolygon: true, drawMarker: true, drawPolyline: true, dragMode: true, removalMode: true, editMode: true });

capaLayout.on('pm:dragstart', () => { posicionOriginalLayout = capaLayout.getBounds(); });

capaLayout.on('pm:dragend', () => {
    if (capaLayout && typeof validarYLimpiarFueraDeLayout === 'function') {
        validarYLimpiarFueraDeLayout('mover');
    }
});
}

// --- RENDERIZADO Y UI ---
const popupUnico = L.popup();
let elementoPopupActivoId = null;

function actualizarPopup(capa, props, fid) {
    const titulo = (props.nombre_propio && props.nombre_propio.trim() !== "") 
        ? props.nombre_propio 
        : (props.nombre_elemento || "Elemento");
    const descripcion = props.descripcion ? props.descripcion : "Sin descripción registrada.";

    const contenidoHTML = `
        <div class="p-2 w-full max-w-xs text-slate-800 box-border overflow-hidden">
            <h3 class="font-bold text-sm text-slate-900 mb-0.5 truncate">${titulo}</h3>
            ${props.nombre_elemento ? `<p class="text-[11px] font-semibold text-blue-600 mb-1 truncate">${props.nombre_elemento}</p>` : ''}
            <p class="text-xs text-slate-600 mb-3 leading-relaxed break-words">${descripcion}</p>
            
            <div class="pt-2 border-t border-slate-100 grid grid-cols-2 gap-1.5 w-full">
                <button type="button" 
                        onclick="event.stopPropagation(); crearBufferUi('${fid}')"
                        class="inline-flex items-center justify-center px-2 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-medium rounded shadow-sm transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    <span>Buffer</span>
                </button>

                <button type="button" 
                        onclick="event.stopPropagation(); medirElementoRiesgoExistente('${fid}')"
                        class="inline-flex items-center justify-center px-2 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-medium rounded shadow-sm transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    <span>Métricas</span>
                </button>

                <button type="button" 
                        onclick="event.stopPropagation(); editarElementoUi('${fid}')"
                        class="inline-flex items-center justify-center px-2 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-[11px] font-medium rounded shadow-sm transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    <span>Editar</span>
                </button>
                
                <button type="button" 
                        onclick="event.stopPropagation(); eliminarElementoUi('${fid}')"
                        class="inline-flex items-center justify-center px-2 py-1.5 bg-red-600 hover:bg-red-700 text-white text-[11px] font-medium rounded shadow-sm transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    <span>Eliminar</span>
                </button>
            </div>
        </div>
    `;

    if (elementoPopupActivoId === fid && popupUnico.isOpen()) {
        popupUnico.setContent(contenidoHTML);
    }
    
    return contenidoHTML;
}

function abrirPopupUnico(capa, props, fid, latlng) {
    elementoPopupActivoId = fid;
    const html = actualizarPopup(capa, props, fid);
    
    let targetLatLng = latlng;
    if (!targetLatLng) {
        if (capa.getLatLng) targetLatLng = capa.getLatLng();
        else if (capa.getBounds) targetLatLng = capa.getBounds().getCenter();
    }

    if (targetLatLng) {
        popupUnico.setLatLng(targetLatLng).setContent(html).openOn(map);
    }
}

function renderizarLeyenda() {
    const contenedor = document.getElementById('lista-leyenda');
    if (!contenedor) return;
    
    contenedor.innerHTML = '';
    
    if (typeof mapaCapas === 'undefined' || Object.keys(mapaCapas).length === 0) {
        contenedor.innerHTML = '<li id="leyenda-vacia" class="text-sm text-gray-400 text-center mt-10 italic">No hay elementos registrados.</li>'; 
        return;
    }

    const grupos = {};

    Object.values(mapaCapas).forEach(capa => {
        const props = (capa.feature && capa.feature.properties) ? capa.feature.properties : {
            id_elemento: capa.id_elemento,
            id_simbologia: capa.id_simbologia,
            nombre_elemento: capa.nombre_elemento,
            nombre_propio: capa.nombre_propio,
            categoria: capa.categoria || 'Otros',
            estilo_defecto: capa.estiloDefecto,
            estilo_personalizado: capa.estiloCustom
        };

        const featureId = capa.featureId || props.id_elemento || capa.id_elemento;
        if (!featureId) return;

        capa.featureId = featureId;

        let estilo = {};
        if (typeof obtenerEstiloVisual === 'function') {
            estilo = obtenerEstiloVisual(props);
        } else {
            estilo = props.estilo_personalizado || props.estilo_defecto || capa.estiloCustom || {};
        }

        let estiloParseado = {};
        if (typeof parsearEstilo === 'function' && props.estilo_personalizado) {
            estiloParseado = parsearEstilo(props.estilo_personalizado);
        } else if (typeof props.estilo_personalizado === 'object' && props.estilo_personalizado !== null) {
            estiloParseado = props.estilo_personalizado;
        }
        
        const esEstiloCustom = Object.keys(estiloParseado).length > 0;
        const tieneNombrePropio = props.nombre_propio && String(props.nombre_propio).trim() !== '';
        
        const tipoGeom = (capa.feature && capa.feature.geometry) ? capa.feature.geometry.type : 'Point';
        const keyLeyenda = (esEstiloCustom || tieneNombrePropio) ? `custom_${featureId}` : `default_${props.id_simbologia}_${tipoGeom}`;
        
        const categoria = props.categoria || 'Otros';
        
        if (!grupos[categoria]) grupos[categoria] = {};
        if (!grupos[categoria][keyLeyenda]) { 
            grupos[categoria][keyLeyenda] = { 
                subcategoria: tieneNombrePropio ? props.nombre_propio : (props.nombre_elemento || 'Elemento'), 
                estilo: estilo, 
                ids: [], 
                esIndividual: (esEstiloCustom || tieneNombrePropio) 
            }; 
        }
        grupos[categoria][keyLeyenda].ids.push(featureId);
    });

    let indexCat = 0;
    for (const [categoria, items] of Object.entries(grupos)) {
        const idCat = `cat-ul-${indexCat}`;
        const idIcon = `cat-icon-${indexCat}`;
        indexCat++;

        const grupoLi = document.createElement('li'); 
        grupoLi.className = 'mb-2 bg-white dark:bg-gray-800 rounded border border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm';
        
        grupoLi.innerHTML = `
            <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 active:bg-gray-200 transition-colors" onclick="toggleAcordeonCategoria('${idCat}', '${idIcon}')">
                <h4 class="text-[11px] sm:text-xs font-bold text-gray-700 dark:text-gray-200 uppercase tracking-wider select-none flex items-center">
                    ${categoria}
                </h4>
                <svg id="${idIcon}" class="w-3.5 h-3.5 text-gray-500 dark:text-gray-400 transition-transform" style="transform: rotate(90deg);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </div>
            <ul id="${idCat}" class="space-y-1 p-2 bg-white dark:bg-gray-800 transition-all"></ul>
        `;
        
        const ul = grupoLi.querySelector('ul');

        for (const [key, data] of Object.entries(items)) {
            let iconHtml = '';
            
            if (data.estilo && data.estilo.isIcon && data.estilo.iconUrl) { 
                iconHtml = `<img src="${data.estilo.iconUrl}" class="w-4 h-4 object-contain">`; 
            } else { 
                const color = (data.estilo && (data.estilo.fillColor || data.estilo.color)) || '#3b82f6'; 
                const patron = (typeof asegurarPatronSVG === 'function' && data.estilo && data.estilo.patron && data.estilo.patron !== 'solido') ? asegurarPatronSVG(data.estilo.patron, color) : color; 
                
                if (key.includes('Line')) {
                    iconHtml = `<div class="w-4 h-1.5 flex-shrink-0" style="background: ${patron}; border-top: 1.5px solid ${color};"></div>`;
                } else {
                    iconHtml = `<div class="w-3.5 h-3.5 rounded-sm border border-gray-400 flex-shrink-0" style="background: ${patron}"></div>`; 
                }
            }

            const badgeCantidad = (!data.esIndividual && data.ids.length > 1) ? `<span class="bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-[9px] font-bold px-1.5 py-0.5 rounded-full ml-1">${data.ids.length}</span>` : '';
            const idsJson = JSON.stringify(data.ids).replace(/"/g, '&quot;');
            const estanVisibles = data.ids.every(id => window.map && mapaCapas[id] && window.map.hasLayer(mapaCapas[id]));

            const liElemento = document.createElement('li'); 
            liElemento.className = "flex items-center space-x-2 p-1 hover:bg-gray-50 dark:hover:bg-gray-700 rounded transition";
            liElemento.innerHTML = `
                <input type="checkbox" ${estanVisibles ? 'checked' : ''} class="w-3 h-3 text-blue-600 bg-gray-100 border-gray-300 rounded cursor-pointer" onclick="typeof toggleVisibilidadGrupo === 'function' ? toggleVisibilidadGrupo(event, '${idsJson}') : null">
                <div class="flex-1 overflow-hidden flex items-center" onclick="typeof centrarGrupo === 'function' ? centrarGrupo('${idsJson}') : null">
                    ${iconHtml}
                    <p class="ml-2 text-[11px] sm:text-xs font-medium text-gray-600 dark:text-gray-300 truncate cursor-pointer select-none" title="${data.subcategoria}">${data.subcategoria}</p>
                    ${badgeCantidad}
                </div>
            `;
            ul.appendChild(liElemento);
        }
        contenedor.appendChild(grupoLi);
    }
}

window.toggleAcordeonCategoria = function(categoriaId, iconoId) {
    const ul = document.getElementById(categoriaId);
    const icono = document.getElementById(iconoId);
    if (ul.classList.contains('hidden')) {
        ul.classList.remove('hidden');
        icono.style.transform = 'rotate(90deg)';
    } else {
        ul.classList.add('hidden');
        icono.style.transform = 'rotate(0deg)';
    }
};

window.toggleVisibilidadGrupo = function(event, idsJson) {
    event.stopPropagation(); const ids = JSON.parse(idsJson.replace(/&quot;/g, '"')); const debeEstarVisible = event.target.checked;
    ids.forEach(id => { const capa = mapaCapas[id]; if (capa) { if (debeEstarVisible && !map.hasLayer(capa)) map.addLayer(capa); else if (!debeEstarVisible && map.hasLayer(capa)) { map.removeLayer(capa); map.closePopup(); } } });
};

window.centrarGrupo = function(idsJson) {
    const ids = JSON.parse(idsJson.replace(/&quot;/g, '"')); const capasActivas = [];
    ids.forEach(id => { const capa = mapaCapas[id]; if (capa && map.hasLayer(capa)) capasActivas.push(capa); });
    if (capasActivas.length === 0) return;
    if (capasActivas.length === 1) { const capa = capasActivas[0]; if (capa.getBounds) map.fitBounds(capa.getBounds()); else if (capa.getLatLng) map.setView(capa.getLatLng(), 17); if (capa.openPopup) capa.openPopup(); } 
    else { const grupoTemporal = L.featureGroup(capasActivas); map.fitBounds(grupoTemporal.getBounds(), { padding: [30, 30] }); }
};

window.crearBufferUi = async function(id) {
    const capa = mapaCapas[id]; 
    if (!capa) return;

    const { value: radio } = await Swal.fire({
        title: 'Crear Área de Amortiguamiento',
        input: 'number',
        inputLabel: 'Radio en metros (ej. 50)',
        inputValue: 50,
        showCancelButton: true,
        confirmButtonText: 'Generar Buffer',
        inputValidator: (value) => {
            if (!value || value <= 0) return 'Ingrese un valor válido mayor a 0';
        }
    });

    if (radio) {
        const geojson = capa.toGeoJSON();
        const bufferGeoJSON = turf.buffer(geojson, Number(radio), {units: 'meters'});

        L.geoJSON(bufferGeoJSON, {
            style: { 
                color: '#ef4444', 
                weight: 2, 
                fillColor: '#ef4444', 
                fillOpacity: 0.2, 
                dashArray: '5,5' 
            }
        }).addTo(map);

        Swal.fire({
            icon: 'success',
            title: 'Análisis Completado',
            text: `Buffer de ${radio}m generado correctamente.`,
            toast: true, position: 'top-end', timer: 3000, showConfirmButton: false
        });
    }
};

window.eliminarElementoUi = async function(id) {
    map.closePopup();
    const capa = mapaCapas[id]; if (!capa) return;
    const confirm = await Swal.fire({ title: '¿Eliminar elemento?', icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33', confirmButtonText: 'Sí, eliminar' });
    if(!confirm.isConfirmed) return;
    if (map.pm) { map.removeLayer(capa); map.fire('pm:remove', { layer: capa, fromUI: true }); }
};

window.exportarCapaSIG = function(formato) {
    if (Object.keys(mapaCapas).length === 0) {
        return Swal.fire('Error', 'No hay elementos en el mapa para exportar', 'error');
    }

    const features = Object.values(mapaCapas).map(capa => {
        let feature = capa.toGeoJSON();
        feature.properties = capa.feature ? capa.feature.properties : {};
        delete feature.properties.estilo_personalizado; 
        return feature;
    });

    const geojsonData = { type: "FeatureCollection", features: features };

    let dataStr, mimeType, extension;

    if (formato === 'geojson') {
        dataStr = JSON.stringify(geojsonData);
        mimeType = "application/json";
        extension = "geojson";
    } else if (formato === 'kml') {
        dataStr = tokml(geojsonData);
        mimeType = "application/vnd.google-earth.kml+xml";
        extension = "kml";
    }

    const blob = new Blob([dataStr], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extraccion_oncc_${new Date().toISOString().split('T')[0]}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

window.editarElementoUi = async function(id) {
    const fid = String(id);
    let capa = mapaCapas[fid]; 
    if (!capa) return;

    map.closePopup();

    if (!capa.feature) capa.feature = { type: 'Feature', properties: {} };
    if (!capa.feature.properties) capa.feature.properties = {};
    const props = capa.feature.properties;

    const esPol = capa instanceof L.Polygon || capa instanceof L.Rectangle; 
    const esLinea = capa instanceof L.Polyline && !esPol; 
    const esPunto = capa instanceof L.Marker || capa instanceof L.CircleMarker;
    const tipoGeom = esPol ? 'Polygon' : (esLinea ? 'Line' : 'Marker');
    
    let opciones = '';
    catalogoSimbolos.forEach(s => {
        const dbTipo = (s.tipo_geometria || '').toLowerCase();
        if ((esPunto && (dbTipo.includes('point') || dbTipo.includes('punto'))) || 
            (esLinea && (dbTipo.includes('line') || dbTipo.includes('línea'))) || 
            (esPol && (dbTipo.includes('polygon') || dbTipo.includes('poligono')))) {
            opciones += `<option value="${s.id_simbologia}" data-cat="${s.categoria}" data-nom="${s.nombre_elemento}" ${(s.id_simbologia == props.id_simbologia) ? 'selected' : ''}>${s.categoria} - ${s.nombre_elemento}</option>`;
        }
    });

    const datosPrevios = { 
        id_simbologia: props.id_simbologia || '', 
        categoria: props.categoria || capa.categoria || '', 
        nombre: props.nombre_elemento || capa.nombre_elemento || '', 
        descripcion: props.descripcion || capa.descripcion || '', 
        nombre_propio: props.nombre_propio || capa.nombre_propio || '', 
        estilo_personalizado: parsearEstilo(props.estilo_personalizado || capa.estiloCustom) 
    };

    const { value: formValues } = await Swal.fire({
        title: 'Editar Propiedades', 
        html: obtenerHtmlFormularioElemento(opciones, tipoGeom, datosPrevios), 
        focusConfirm: false, 
        showCancelButton: true, 
        confirmButtonText: 'Guardar Cambios', 
        cancelButtonText: 'Cancelar',
        preConfirm: () => {
            if (!validarFormularioSwal()) return false;
            const sel = document.getElementById('swal-simbologia'); 
            const opt = sel ? sel.options[sel.selectedIndex] : null;
            const nombrePropioVal = document.getElementById('swal-nombre-propio').value.trim();
            return { 
                id_simbologia: sel ? sel.value : '', 
                categoria: opt ? opt.getAttribute('data-cat') : '', 
                nombre_elemento: opt ? opt.getAttribute('data-nom') : '', 
                desc: document.getElementById('swal-desc').value, 
                nombrePropio: nombrePropioVal, 
                estiloCustom: recolectarEstilosSwal() 
            };
        }
    });

    if (formValues) {
        historialAcciones.push({ 
            tipo: 'editar_elemento', 
            id: fid, 
            capa: capa, 
            propsAnteriores: JSON.parse(JSON.stringify(props)), 
            actualizacionAnterior: estadoCambios.actualizados[fid] ? JSON.parse(JSON.stringify(estadoCambios.actualizados[fid])) : null 
        }); 
        actualizarBotonDeshacer();

        props.id_simbologia = formValues.id_simbologia; 
        props.categoria = formValues.categoria; 
        props.nombre_elemento = formValues.nombre_elemento; 
        props.descripcion = formValues.desc; 
        props.nombre_propio = formValues.nombrePropio; 
        props.estilo_personalizado = formValues.estiloCustom;

        capa.id_simbologia = formValues.id_simbologia;
        capa.nombre_elemento = formValues.nombre_elemento;
        capa.nombre_propio = formValues.nombrePropio;
        capa.descripcion = formValues.desc;
        capa.estiloCustom = formValues.estiloCustom;

        if (fid.startsWith('temp_')) { 
            let idx = estadoCambios.creados.findIndex(c => c.tempId === fid); 
            if (idx !== -1) { 
                Object.assign(estadoCambios.creados[idx], { 
                    id_simbologia: formValues.id_simbologia, 
                    descripcion: formValues.desc, 
                    nombre_propio: formValues.nombrePropio, 
                    estiloCustom: formValues.estiloCustom 
                }); 
            } 
        } else { 
            if (!estadoCambios.actualizados[fid]) estadoCambios.actualizados[fid] = {}; 
            Object.assign(estadoCambios.actualizados[fid], { 
                id_simbologia: formValues.id_simbologia, 
                descripcion: formValues.desc, 
                nombre_propio: formValues.nombrePropio, 
                estilo_personalizado: formValues.estiloCustom 
            }); 
        }

        const estVisual = obtenerEstiloVisual(props);
        const esPuntoCapa = capa instanceof L.Marker || capa instanceof L.CircleMarker;

        if (esPuntoCapa) {
            const latlng = capa.getLatLng();
            if (estVisual.isIcon && estVisual.iconUrl) {
                if (capa instanceof L.CircleMarker) {
                    map.removeLayer(capa);
                    const newMarker = L.marker(latlng, {
                        icon: L.icon({ iconUrl: estVisual.iconUrl, iconSize: estVisual.iconSize || [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -15] })
                    });
                    newMarker.feature = capa.feature; newMarker.featureId = fid; newMarker.id_elemento = capa.id_elemento;
                    newMarker.id_simbologia = capa.id_simbologia; newMarker.nombre_elemento = capa.nombre_elemento;
                    newMarker.nombre_propio = capa.nombre_propio; newMarker.descripcion = capa.descripcion; newMarker.estiloCustom = capa.estiloCustom;
                    newMarker.on('click', function(e) { abrirPopupUnico(newMarker, props, fid, e.latlng); });
                    newMarker.addTo(map); mapaCapas[fid] = newMarker; capa = newMarker;
                } else if (capa instanceof L.Marker) {
                    capa.setIcon(L.icon({ iconUrl: estVisual.iconUrl, iconSize: estVisual.iconSize || [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -15] }));
                }
            } else {
                if (capa instanceof L.Marker) {
                    map.removeLayer(capa);
                    const newCircle = L.circleMarker(latlng, {
                        radius: estVisual.radius || 7,
                        color: estVisual.color || '#3388ff',
                        fillColor: estVisual.fillColor || estVisual.color || '#3388ff',
                        fillOpacity: estVisual.fillOpacity !== undefined ? estVisual.fillOpacity : 0.8,
                        weight: estVisual.weight !== undefined ? estVisual.weight : 2
                    });
                    newCircle.feature = capa.feature; newCircle.featureId = fid; newCircle.id_elemento = capa.id_elemento;
                    newCircle.id_simbologia = capa.id_simbologia; newCircle.nombre_elemento = capa.nombre_elemento;
                    newCircle.nombre_propio = capa.nombre_propio; newCircle.descripcion = capa.descripcion; newCircle.estiloCustom = capa.estiloCustom;
                    newCircle.on('click', function(e) { abrirPopupUnico(newCircle, props, fid, e.latlng); });
                    newCircle.addTo(map); mapaCapas[fid] = newCircle; capa = newCircle;
                } else if (capa instanceof L.CircleMarker) {
                    capa.setStyle({
                        radius: estVisual.radius || 7,
                        color: estVisual.color || '#3388ff',
                        fillColor: estVisual.fillColor || estVisual.color || '#3388ff',
                        fillOpacity: estVisual.fillOpacity !== undefined ? estVisual.fillOpacity : 0.8,
                        weight: estVisual.weight !== undefined ? estVisual.weight : 2
                    });
                }
            }
        } else if (typeof capa.setStyle === 'function') {
            capa.setStyle({ 
                color: estVisual.color || '#3388ff', 
                fillColor: asegurarPatronSVG(estVisual.patron, estVisual.color || '#3388ff'), 
                weight: estVisual.weight !== undefined ? estVisual.weight : 2, 
                dashArray: estVisual.dashArray || null, 
                fillOpacity: 0.8 
            }); 
        } 

        actualizarPopup(capa, props, fid); 
        renderizarLeyenda(); 
        escalarEstilosPorZoom();
        
        Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 }).fire({ 
            icon: 'success', 
            title: 'Elemento Actualizado' 
        });
    }
};

function cargarCapasDelServidor(mapaId, opcionesGeoJson) {
    fetch(`/geomatica/mapas/${mapaId}`)
        .then(res => {
            if (!res.ok) throw new Error("Error al consultar el mapa");
            return res.json();
        })
        .then(data => {
            if (data.limites_layout && Array.isArray(data.limites_layout) && data.limites_layout.length === 2) {
                map.fitBounds(data.limites_layout);

                if (typeof capaLayout !== 'undefined' && capaLayout) {
                    map.removeLayer(capaLayout);
                }
                
                capaLayout = L.rectangle(data.limites_layout, { 
                    color: '#dc2626', 
                    weight: 3, 
                    fillOpacity: 0.05, 
                    dashArray: '8, 8', 
                    interactive: true 
                }).addTo(map);
                
                capaLayout.isLayout = true;
                posicionOriginalLayout = capaLayout.getBounds();
                
                if (typeof estadoCambios !== 'undefined') {
                    estadoCambios.layout = capaLayout.getBounds();
                }

                capaLayout.options.pmIgnore = false; 
                if (map.pm) {
                    map.pm.addControls({ 
                        drawRectangle: true, 
                        drawPolygon: true, 
                        drawMarker: true, 
                        drawPolyline: true, 
                        dragMode: true, 
                        removalMode: true, 
                        editMode: true 
                    });
                }

                capaLayout.on('pm:dragstart', () => { 
                    posicionOriginalLayout = capaLayout.getBounds(); 
                });
                
                capaLayout.on('pm:dragend', () => {
                    if (typeof validarYLimpiarFueraDeLayout === 'function') {
                        validarYLimpiarFueraDeLayout('mover');
                    }
                });
            }

            if (data.poligonal_comunidad) {
                if (typeof capaComunidad !== 'undefined' && capaComunidad) {
                    map.removeLayer(capaComunidad);
                }
                
                // Al cargar L.geoJSON de un MultiPolygon, Leaflet crea un FeatureGroup con los polígonos dentro.
                capaComunidad = L.geoJSON(data.poligonal_comunidad, {
                    // Mantenemos tu estilo original (puedes cambiar el #ff7800 si no quieres que se vea naranja/amarillo)
                    style: { color: "#000000", weight: 3, fillOpacity: 0.1, dashArray: '5, 5' },
                    
                    // ELIMINAMOS pmIgnore: true y usamos onEachFeature para iterar sobre las geometrías hijas
                    onEachFeature: function(feature, layer) {
                        layer.isComunidad = true; // Etiqueta vital para que gestionarCambioCapa funcione
                        layer.options.pmIgnore = false; // Forzamos a Geoman a reconocer la capa
                        
                        // Re-vinculamos los eventos de guardado y actualización
                        layer.on('pm:update', gestionarCambioCapa);
                        layer.on('pm:cut', gestionarCambioCapa);
                    }
                }).addTo(map);

                // Nos aseguramos de que el grupo padre tampoco sea ignorado por las herramientas globales de Geoman
                capaComunidad.options.pmIgnore = false;

                if (typeof capaLayout === 'undefined' || !capaLayout || !map.hasLayer(capaLayout)) {
                    map.fitBounds(capaComunidad.getBounds());
                }
            }

            if (data.elementos_riesgo && Array.isArray(data.elementos_riesgo)) {
                if (typeof drawnItems !== 'undefined') {
                    drawnItems.clearLayers();
                }

                if (typeof mapaCapas !== 'undefined' && mapaCapas !== null) {
                    Object.keys(mapaCapas).forEach(key => delete mapaCapas[key]);
                }

                data.elementos_riesgo.forEach(feature => {
                    const props = feature.properties || {};
                    const idElemento = props.id_elemento;
                    
                    let baseConfig = (typeof opcionesGeoJson === 'function') 
                        ? opcionesGeoJson(props) 
                        : (opcionesGeoJson || {});

                    const prevOnEachFeature = baseConfig.onEachFeature;

                    const mergedConfig = Object.assign({}, baseConfig, {
                        onEachFeature: function(feat, layer) {
                            if (typeof prevOnEachFeature === 'function') {
                                prevOnEachFeature(feat, layer);
                            }

                            const propiedades = feat.properties || props;
                            layer.feature = feat;
                            layer.featureId = idElemento;
                            layer.id_elemento = idElemento;
                            layer.id_simbologia = propiedades.id_simbologia;
                            layer.nombre_elemento = propiedades.nombre_elemento || "";
                            layer.nombre_propio = propiedades.nombre_propio || "";
                            layer.descripcion = propiedades.descripcion || "";
                            layer.estiloCustom = propiedades.estilo_personalizado;

                            layer.on('click', function(e) {
                                if (typeof abrirPopupUnico === 'function') {
                                    abrirPopupUnico(layer, propiedades, idElemento, e.latlng);
                                }
                            });

                            if (typeof mapaCapas !== 'undefined' && mapaCapas !== null) {
                                mapaCapas[idElemento] = layer;
                            }

                            if (typeof drawnItems !== 'undefined') {
                                drawnItems.addLayer(layer);
                            } else {
                                layer.addTo(map);
                            }
                        }
                    });

                    L.geoJSON(feature, mergedConfig);
                });

                if (typeof renderizarLeyenda === 'function') {
                    renderizarLeyenda();
                }
            }
        })
        .catch(err => console.error("Error cargando capas del servidor:", err));
}

async function gestionarCambioCapa(e) {
    const capa = e.layer || e.target; 
    if (capaLayout && !isLayerInsideLayout(capa, capaLayout)) {
        await Swal.fire('Fuera de Rango', 'El elemento no puede colocarse fuera del marco del Layout.', 'warning');
        if (capa.feature && capa.feature.geometry) { const tempLayer = L.geoJSON(capa.feature.geometry); const restLayer = tempLayer.getLayers()[0]; if (capa.setLatLngs && restLayer.getLatLngs) capa.setLatLngs(restLayer.getLatLngs()); else if (capa.setLatLng && restLayer.getLatLng) capa.setLatLng(restLayer.getLatLng()); }
        return;
    }

    if (capa.isComunidad) {
        let nuevaCom;
        if (capaComunidad && typeof capaComunidad.eachLayer === 'function') {
            const polys = []; capaComunidad.eachLayer(l => { const geom = l.toGeoJSON().geometry; if (geom.type === 'Polygon') polys.push(geom.coordinates); else if (geom.type === 'MultiPolygon') polys.push(...geom.coordinates); });
            nuevaCom = polys.length > 1 ? { type: "MultiPolygon", coordinates: polys } : { type: "Polygon", coordinates: polys[0] };
        } else nuevaCom = (capaComunidad || capa).toGeoJSON().geometry;
        estadoCambios.comunidad = nuevaCom; if(capa.feature) capa.feature.geometry = nuevaCom; return;
    }

    if (capa.featureId) { 
        const nuevaGeom = capa.toGeoJSON().geometry; capa.feature.geometry = nuevaGeom; let fid = String(capa.featureId); 
        if (fid.startsWith('temp_')) { let idx = estadoCambios.creados.findIndex(c => c.tempId === fid); if (idx !== -1) estadoCambios.creados[idx].geometria = nuevaGeom; } 
        else { if (!estadoCambios.actualizados[fid]) estadoCambios.actualizados[fid] = {}; estadoCambios.actualizados[fid].geometria = nuevaGeom; }
    }
}

document.addEventListener("DOMContentLoaded", function() {
    if (typeof lucide !== 'undefined') { lucide.createIcons(); }
    document.getElementById('btn-deshacer').addEventListener('click', deshacerUltimaAccion);
    document.getElementById('btn-descartar').addEventListener('click', function() { if (!hayCambiosPendientes()) return Swal.fire('Sin cambios', '', 'info'); Swal.fire({ title: '¿Descartar cambios no guardados?', icon: 'warning', showCancelButton: true, confirmButtonText: 'Sí, descartar' }).then(res => { if (res.isConfirmed) location.reload(); }); });
    
    document.getElementById('btn-limpiar-todo').addEventListener('click', function() {
        Swal.fire({ title: '¿BORRAR TODO EL MAPA?', icon: 'error', showCancelButton: true, confirmButtonColor: '#d33', confirmButtonText: 'Sí, limpiar mapa' }).then((result) => {
            if (result.isConfirmed) {
                for (let id of Object.keys(mapaCapas)) { let fid = String(id); if (fid.startsWith('temp_')) { estadoCambios.creados = estadoCambios.creados.filter(c => c.tempId !== fid); } else { estadoCambios.eliminados.add(fid); delete estadoCambios.actualizados[fid]; } map.removeLayer(mapaCapas[fid]); delete mapaCapas[fid]; }
                renderizarLeyenda(); if (capaComunidad) { map.removeLayer(capaComunidad); capaComunidad = null; }
                estadoCambios.comunidad = "ELIMINAR"; geometriaComunidadOriginal = null; historialAcciones.length = 0; actualizarBotonDeshacer();
            }
        });
    });

    // 🔴 Aquí consumimos la variable del objeto global
    const mapaId = window.ONCC_CONFIG.mapaId;
    fetch(window.ONCC_CONFIG.urlCatalogo).then(res => res.json()).then(data => { catalogoSimbolos = data; }).catch(err => console.error(err));

    const limitesMundo = L.latLngBounds(L.latLng(-85, -180), L.latLng(85, 180));
    window.map = L.map('map', { maxBounds: limitesMundo, maxBoundsViscosity: 1.0, minZoom: 3 }).setView([7.5, -66.0], ZOOM_BASE_ESCALA);
    L.control.scale({
        position: 'bottomleft',
        metric: true,
        imperial: false,
        maxWidth: 200
    }).addTo(window.map);
   
    const satelitePuro = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google Maps'
    }).addTo(map);

    const roadmapLimpio = L.tileLayer('https://{s}.google.com/vt/lyrs=m&apistyle=s.e:l|p.v:off|s.t:1|p.v:off&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google Maps'
    });

    const overlayEtiquetasYCalles = L.tileLayer('https://{s}.google.com/vt/lyrs=h&apistyle=s.t:1|p.v:off&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google Maps'
    });

    const mapasBase = {
        "🛰️ Satélite": satelitePuro,
        "🗺️ Callejero": roadmapLimpio
    };

    const capasSuperpuestas = {
        "🔤 Superponer Nombres, Calles y Negocios (Capa h)": overlayEtiquetasYCalles
    };

    L.control.layers(mapasBase, capasSuperpuestas, { 
        position: 'topright', 
        collapsed: true 
    }).addTo(map);

    map.pm.setLang('es');
    map.pm.addControls({ position: 'topleft', drawRectangle: false, drawPolygon: false, drawMarker: false, drawPolyline: false, drawCircle: false, drawCircleMarker: false, drawText: false, editMode: true, dragMode: false, cutPolygon: false, removalMode: true });

    map.on('pm:globaleditmodetoggled', function(e) { if (e.enabled && capaLayout) { capaLayout.pm.disable(); } });

    async function escalarLayout(factor) {
        if (!capaLayout) return Swal.fire('Sin Marco', 'Primero debe insertar un marco de Layout.', 'info');
        posicionOriginalLayout = capaLayout.getBounds();
        const bounds = capaLayout.getBounds(); const center = bounds.getCenter();
        const latDiff = (bounds.getNorth() - bounds.getSouth()) * factor; const lngDiff = (bounds.getEast() - bounds.getWest()) * factor;
        capaLayout.setBounds(L.latLngBounds(L.latLng(center.lat - latDiff/2, center.lng - lngDiff/2), L.latLng(center.lat + latDiff/2, center.lng + lngDiff/2)));
        estadoCambios.layout = capaLayout.getBounds(); 
        await validarYLimpiarFueraDeLayout('redimensionar');
    }

    document.getElementById('btn-agrandar-layout').addEventListener('click', () => escalarLayout(1.15));
    document.getElementById('btn-reducir-layout').addEventListener('click', () => escalarLayout(0.85));
    // INSERCIÓN DE LAYOUT (REQUERIMIENTO 2)
document.getElementById('btn-insertar-layout').addEventListener('click', async function() {
if (capaLayout) return Swal.fire('Layout Existente', 'Ya existe un marco. Puedes arrastrarlo o eliminarlo con el botón de borrar de la barra.', 'info');

const ratio = parseFloat(document.getElementById('select-formato-layout').value) || 1.414;
const center = map.getCenter(); 
const bounds = map.getBounds(); 
const latDiff = (bounds.getNorth() - bounds.getSouth()) * 0.40; 
const lngDiff = latDiff * ratio;

const nuevosLimites = L.latLngBounds(
    L.latLng(center.lat - latDiff, center.lng - lngDiff),
    L.latLng(center.lat + latDiff, center.lng + lngDiff)
);

// Creamos un rectángulo virtual (sin añadir al mapa) para evaluar colisiones
const tempLayout = L.rectangle(nuevosLimites);
let elementosFuera = [];

Object.values(mapaCapas).forEach(el => {
    if (!isLayerInsideLayout(el, tempLayout)) elementosFuera.push(el);
});

if (capaComunidad && !isLayerInsideLayout(capaComunidad, tempLayout)) {
    elementosFuera.push(capaComunidad);
}

if (elementosFuera.length > 0) {
    const result = await Swal.fire({
        title: 'Atención: Elementos fuera del Layout',
        text: `Al insertar este nuevo layout, hay ${elementosFuera.length} elemento(s) que quedarán por fuera y SE VAN A ELIMINAR. ¿Deseas continuar o cancelar para intentar otro formato?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, eliminar e insertar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        elementosFuera.forEach(el => {
            if (el === capaComunidad) {
                map.removeLayer(capaComunidad); 
                capaComunidad = null; 
                estadoCambios.comunidad = "ELIMINAR";
            } else {
                let fid = String(el.featureId);
                if (fid.startsWith('temp_')) { 
                    estadoCambios.creados = estadoCambios.creados.filter(c => c.tempId !== fid); 
                } else { 
                    estadoCambios.eliminados.add(fid); 
                    delete estadoCambios.actualizados[fid]; 
                }
                map.removeLayer(el); 
                delete mapaCapas[fid];
            }
        });
        if (typeof renderizarLeyenda === 'function') renderizarLeyenda();
        insertarLayoutEnMapa(nuevosLimites);
        Swal.fire('Proceso Completado', `Se insertó el layout y se eliminaron ${elementosFuera.length} elemento(s).`, 'success');
    }
} else {
    insertarLayoutEnMapa(nuevosLimites);
    Swal.fire({ icon: 'success', title: 'Layout Insertado', text: 'Ya puedes dibujar dentro. Usa el botón de arrastrar (Mano) para moverlo.', timer: 2500, showConfirmButton: false });
}
});

    map.on('zoom', escalarEstilosPorZoom);
    map.pm.setGlobalOptions({ 
        snappable: true, 
        snapDistance: 20, 
        snapMiddle: true, 
        allowSelfIntersection: false, 
        preventMarkerRemoval: false,
        hintlineStyle: { color: '#facc15', dashArray: '5,5', weight: 2 }, 
        templineStyle: { color: '#facc15', weight: 3 }, 
        pathOptions: { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.4 } 
    });

    const opcionesGeoJson = {
        // Manejo de estilos para Líneas y Polígonos
        style: function (feature) {
            const est = obtenerEstiloVisual(feature.properties);
            const color = est.color || '#3388ff';
            const fillColor = (typeof asegurarPatronSVG === 'function' && est.patron && est.patron !== 'solido') 
                ? asegurarPatronSVG(est.patron, color) 
                : (est.fillColor || color);
            
            return {
                color: color,
                fillColor: fillColor,
                fillOpacity: est.fillOpacity !== undefined ? est.fillOpacity : 0.6,
                weight: est.weight || 3,
                dashArray: est.dashArray || null
            };
        },

        // Manejo de Marcadores (Ícono personalizado o Marcador Vectorial CircleMarker)
        pointToLayer: function (feature, latlng) {
            const est = obtenerEstiloVisual(feature.properties);

            if (est && est.isIcon && est.iconUrl) {
                const iconoCustom = L.icon({
                    iconUrl: est.iconUrl,
                    iconSize: est.iconSize || [30, 30],
                    iconAnchor: [15, 15],
                    popupAnchor: [0, -15]
                });
                return L.marker(latlng, { icon: iconoCustom });
            }

            return L.circleMarker(latlng, {
                radius: est.radius || 7,
                color: est.color || '#3388ff',
                fillColor: est.fillColor || est.color || '#3388ff',
                fillOpacity: est.fillOpacity !== undefined ? est.fillOpacity : 0.8,
                weight: est.weight !== undefined ? est.weight : 2
            });
        },

        // Asignación de propiedades y evento de clic unificado
        onEachFeature: function (feature, layer) {
            const props = feature.properties;
            const idElemento = props.id_elemento || props.id;
            
            if (props) {
                layer.feature = feature;
                layer.featureId = idElemento;
                layer.id_elemento = idElemento;
                layer.id_simbologia = props.id_simbologia;
                layer.nombre_elemento = props.nombre_elemento || "";
                layer.nombre_propio = props.nombre_propio || "";
                layer.descripcion = props.descripcion || "";
                layer.estiloCustom = props.estilo_personalizado;

                layer.on('click', function(e) {
                    abrirPopupUnico(layer, props, idElemento, e.latlng);
                });

                if (typeof mapaCapas !== 'undefined') {
                    mapaCapas[idElemento] = layer;
                }
            }
        }
    };

    // Cargar capas iniciales del backend
    cargarCapasDelServidor(mapaId, opcionesGeoJson);

    // --- CREACIÓN DE NUEVO ELEMENTO (GEOMAN) ---
    map.on('pm:create', async function(e) {
        const capaOriginal = e.layer; 
        const geojson = capaOriginal.toGeoJSON().geometry; 
        const tipoFigura = e.shape;
        map.removeLayer(capaOriginal); 

        if (!capaLayout) return Swal.fire('Sin Marco', 'Debe insertar el marco de layout antes de dibujar.', 'warning');
        if (!isLayerInsideLayout(capaOriginal, capaLayout)) return Swal.fire('Fuera de Rango', 'El elemento trazado sobrepasa los límites del Layout.', 'error');

        let opciones = '<option value="">Seleccione un símbolo base...</option>';
        catalogoSimbolos.forEach(s => {
            const dbTipo = (s.tipo_geometria || '').toLowerCase();
            if (((tipoFigura === 'Marker' || tipoFigura === 'CircleMarker') && (dbTipo.includes('point') || dbTipo.includes('punto'))) || 
                ((tipoFigura === 'Line' || tipoFigura === 'Polyline') && (dbTipo.includes('line') || dbTipo.includes('línea'))) || 
                ((tipoFigura === 'Polygon' || tipoFigura === 'Rectangle') && (dbTipo.includes('polygon') || dbTipo.includes('poligono')))) { 
                opciones += `<option value="${s.id_simbologia}" data-cat="${s.categoria}" data-nom="${s.nombre_elemento}">${s.categoria} - ${s.nombre_elemento}</option>`; 
            }
        });

        const { value: formValues } = await Swal.fire({
            title: 'Registrar Elemento', 
            html: obtenerHtmlFormularioElemento(opciones, tipoFigura), 
            focusConfirm: false, 
            showCancelButton: true, 
            confirmButtonText: 'Añadir al Mapa', 
            cancelButtonText: 'Descartar',
            preConfirm: () => {
                const modo = document.getElementById('swal-modo')?.value || 'elemento';
                if (modo === 'comunidad') return { modo: 'comunidad' };
                const idSimb = document.getElementById('swal-simbologia').value;
                if (!idSimb) { Swal.showValidationMessage('Debe seleccionar una Simbología.'); return false; }
                if (!validarFormularioSwal()) return false;
                const sel = document.getElementById('swal-simbologia'); const opt = sel.options[sel.selectedIndex];
                const simboloCatalogo = catalogoSimbolos.find(s => s.id_simbologia.toString() === idSimb);
                const nombrePropioVal = document.getElementById('swal-nombre-propio').value.trim();
                return { 
                    modo: 'elemento', 
                    id_simb: idSimb, 
                    desc: document.getElementById('swal-desc').value, 
                    cat: opt.getAttribute('data-cat'), 
                    nom: opt.getAttribute('data-nom'), 
                    nombrePropio: nombrePropioVal, 
                    estiloCustom: recolectarEstilosSwal(), 
                    estiloDefecto: simboloCatalogo ? parsearEstilo(simboloCatalogo.estilo_defecto) : {} 
                };
            }
        });

        if (formValues) {
            if (formValues.modo === 'comunidad') {
                if (capaComunidad) {
                    const confirm = await Swal.fire({ 
                        title: 'Comunidad ya definida', 
                        text: '¿Desea reemplazarla o añadir este nuevo trazo (MultiPolígono)?', 
                        icon: 'question', 
                        showCancelButton: true, 
                        showDenyButton: true, 
                        confirmButtonText: 'Añadir (Multi)', 
                        denyButtonText: 'Reemplazar', 
                        cancelButtonText: 'Cancelar' 
                    });
                    if (confirm.isConfirmed) { 
                        capaOriginal.setStyle({ color: '#000000', weight: 3, fillOpacity: 0.1, dashArray: '5, 5' }); 
                        capaOriginal.isComunidad = true; 
                        capaOriginal.on('pm:update', gestionarCambioCapa); 
                        if (!(capaComunidad instanceof L.FeatureGroup)) { 
                            map.removeLayer(capaComunidad); 
                            capaComunidad = L.featureGroup([capaComunidad]).addTo(map); 
                        } 
                        capaComunidad.addLayer(capaOriginal); 
                        gestionarCambioCapa({ layer: capaComunidad }); 
                        return; 
                    } else if (confirm.isDenied) { 
                        map.removeLayer(capaComunidad); 
                        capaComunidad = null; 
                    } else return;
                }
                capaOriginal.setStyle({ color: '#000000', weight: 3, fillOpacity: 0.1, dashArray: '5, 5' }); 
                capaOriginal.addTo(map); 
                capaOriginal.isComunidad = true; 
                capaOriginal.feature = capaOriginal.feature || {}; 
                capaOriginal.feature.geometry = geojson; 
                capaOriginal.on('pm:update', gestionarCambioCapa); 
                capaComunidad = capaOriginal; 
                estadoCambios.comunidad = geojson; 
            } else {
                const tempId = 'temp_' + Date.now(); 
                const datosCreacion = { 
                    tempId: tempId, 
                    id_simbologia: formValues.id_simb, 
                    descripcion: formValues.desc, 
                    nombre_propio: formValues.nombrePropio, 
                    geometria: geojson, 
                    estiloCustom: formValues.estiloCustom 
                }; 
                estadoCambios.creados.push(datosCreacion);

                const featureGeoJson = { 
                    "type": "Feature", 
                    "properties": { 
                        "id": tempId, 
                        "id_simbologia": formValues.id_simb, 
                        "nombre_elemento": formValues.nom, 
                        "categoria": formValues.cat, 
                        "descripcion": formValues.desc, 
                        "nombre_propio": formValues.nombrePropio, 
                        "estilo_defecto": formValues.estiloDefecto, 
                        "estilo_personalizado": formValues.estiloCustom 
                    }, 
                    "geometry": geojson 
                };

                const tempCapaGroup = L.geoJSON(featureGeoJson, opcionesGeoJson).addTo(map); 
                let capaAgregada = null; 
                tempCapaGroup.eachLayer(l => capaAgregada = l);

                if (capaAgregada) {
                    capaAgregada.featureId = tempId;
                    capaAgregada.id_elemento = tempId;
                    capaAgregada.id_simbologia = formValues.id_simb;
                    capaAgregada.nombre_elemento = formValues.nom;
                    capaAgregada.nombre_propio = formValues.nombrePropio;
                    capaAgregada.descripcion = formValues.desc;
                    capaAgregada.estiloCustom = formValues.estiloCustom;

                    mapaCapas[tempId] = capaAgregada;

                    capaAgregada.on('click', function(e) {
                        abrirPopupUnico(capaAgregada, featureGeoJson.properties, tempId, e.latlng);
                    });
                }

                historialAcciones.push({ tipo: 'crear_elemento', id: tempId, capa: capaAgregada, datosCreacion: datosCreacion }); 
                actualizarBotonDeshacer(); 
                renderizarLeyenda(); 
                escalarEstilosPorZoom();
            }
        }
    });

    // --- ELIMINACIÓN DE ELEMENTOS ---
    map.on('pm:remove', async function(e) { 
        map.closePopup();
        const capa = e.layer;

        // 1. LÓGICA EXCLUSIVA DEL LAYOUT
        if (capa.isLayout) {
            capaLayout = null; 
            posicionOriginalLayout = null;
            if (typeof estadoCambios !== 'undefined') estadoCambios.layout = "ELIMINAR"; 
            
            // Bloqueamos las herramientas porque ya no hay marco
            map.pm.addControls({ drawRectangle: false, drawPolygon: false, drawMarker: false, drawPolyline: false, dragMode: false, editMode: false });

            const elementosIds = Object.keys(mapaCapas);
            
            if (elementosIds.length > 0) {
                const result = await Swal.fire({
                    title: 'Layout Eliminado',
                    text: `Has eliminado el layout. ¿Deseas eliminar también los ${elementosIds.length} elementos internos dibujados? (La comunidad NO será borrada).`,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Sí, eliminar todo',
                    cancelButtonText: 'No, conservarlos'
                });

                if (result.isConfirmed) {
                    elementosIds.forEach(fid => {
                        const el = mapaCapas[fid];
                        if (fid.startsWith('temp_')) {
                            estadoCambios.creados = estadoCambios.creados.filter(c => c.tempId !== fid);
                        } else {
                            estadoCambios.eliminados.add(fid);
                            delete estadoCambios.actualizados[fid];
                        }
                        map.removeLayer(el);
                        delete mapaCapas[fid];
                    });
                    if (typeof renderizarLeyenda === 'function') renderizarLeyenda();
                    Swal.fire('Elementos eliminados', 'El layout y sus elementos fueron removidos.', 'success');
                } else {
                    Swal.fire('Elementos conservados', 'Aún tienes elementos en el mapa sin layout.', 'info');
                }
            } else {
                Swal.fire({ icon: 'info', title: 'Marco Eliminado', text: 'El marco fue removido de forma segura.', timer: 2000, showConfirmButton: false });
            }
            return; // Salimos aquí para que no ejecute lo de abajo
        }

        // 2. LÓGICA DE LA COMUNIDAD
        if (capa.isComunidad) {
            if (capaComunidad instanceof L.FeatureGroup) { 
                capaComunidad.removeLayer(capa); 
                if (capaComunidad.getLayers().length === 0) { 
                    capaComunidad = null; 
                    estadoCambios.comunidad = "ELIMINAR"; 
                } else { 
                    gestionarCambioCapa({ layer: capaComunidad }); 
                } 
            } else { 
                capaComunidad = null; 
                estadoCambios.comunidad = "ELIMINAR"; 
            } 
            return;
        }

        // 3. LÓGICA DE LOS ELEMENTOS DIBUJADOS
        if (capa.featureId) { 
            let fid = String(capa.featureId); 
            let datosCreacion = null; 
            let datosActualizacion = null;
            if (fid.startsWith('temp_')) { 
                datosCreacion = estadoCambios.creados.find(c => c.tempId === fid); 
                estadoCambios.creados = estadoCambios.creados.filter(c => c.tempId !== fid); 
            } else { 
                estadoCambios.eliminados.add(fid); 
                if(estadoCambios.actualizados[fid]) { 
                    datosActualizacion = estadoCambios.actualizados[fid]; 
                    delete estadoCambios.actualizados[fid]; 
                } 
            }
            historialAcciones.push({ tipo: 'eliminar_elemento', id: fid, capa: capa, propsAnteriores: capa.feature.properties, datosCreacion: datosCreacion, datosActualizacion: datosActualizacion });
            actualizarBotonDeshacer(); 
            delete mapaCapas[fid]; 
            renderizarLeyenda();
        }
    });

    // --- CORTE DE POLÍGONOS (RECORTAR COMUNIDAD) ---
    map.on('pm:cut', function(e) {
        if (e.originalLayer && e.originalLayer.isComunidad) {
            const nuevaCapa = e.layer; 
            nuevaCapa.isComunidad = true; 
            nuevaCapa.on('pm:update', gestionarCambioCapa); 
            capaComunidad = nuevaCapa; 
            const polys = []; 
            nuevaCapa.eachLayer(l => { 
                const geom = l.toGeoJSON().geometry; 
                if (geom.type === 'Polygon') polys.push(geom.coordinates); 
                else if (geom.type === 'MultiPolygon') polys.push(...geom.coordinates); 
            });
            estadoCambios.comunidad = { type: "MultiPolygon", coordinates: polys }; 
            if (capaComunidad.feature) capaComunidad.feature.geometry = estadoCambios.comunidad;
        }
    });

    window.toggleMenuHerramientas = function() {
        const menu = document.getElementById("menu-herramientas-contenido");
        if (menu) {
            menu.classList.toggle("hidden");
        }
    };

    window.cerrarMenuHerramientas = function() {
        const menu = document.getElementById("menu-herramientas-contenido");
        if (menu && !menu.classList.contains("hidden")) {
            menu.classList.add("hidden");
        }
    };

    const btnMenuHerramientas = document.getElementById('btn-menu-herramientas');
    if (btnMenuHerramientas) {
        btnMenuHerramientas.addEventListener('click', function(event) {
            event.stopPropagation(); 
            window.toggleMenuHerramientas();
        });
    }

    document.addEventListener("click", function(event) {
        const dropdown = document.getElementById("menu-herramientas-contenido");
        const button = document.getElementById("btn-menu-herramientas");
        
        if (dropdown && !dropdown.classList.contains("hidden")) {
            const clicEnDropdown = dropdown.contains(event.target);
            const clicEnBoton = button ? button.contains(event.target) : false;
            
            if (!clicEnDropdown && !clicEnBoton) {
                window.cerrarMenuHerramientas();
            }
        }
    });

    let modoAnalisisActual = null;
    let puntosAnalisis = [];
    let capaAnalisisGroup = null;

    function asegurarCapaAnalisis() {
        if (!capaAnalisisGroup) {
            capaAnalisisGroup = L.featureGroup().addTo(window.map);
        }
    }

    function ejecutarPasoAnalisis(e) {
        if (!modoAnalisisActual) return;
        puntosAnalisis.push([e.latlng.lng, e.latlng.lat]);

        L.circleMarker(e.latlng, {
            color: '#2563eb',
            radius: 5,
            fillColor: '#ffffff',
            fillOpacity: 1
        }).addTo(capaAnalisisGroup);

        if (puntosAnalisis.length > 1 && modoAnalisisActual === 'linea') {
            const coordsLatLon = puntosAnalisis.map(p => [p[1], p[0]]);
            L.polyline(coordsLatLon, { color: '#2563eb', weight: 3, dashArray: '5,5' }).addTo(capaAnalisisGroup);

            const line = turf.lineString(puntosAnalisis);
            const metros = turf.length(line, { units: 'meters' });
            const texto = metros > 1000 ? `${(metros / 1000).toFixed(2)} km` : `${metros.toFixed(1)} metros`;

            Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 3000 }).fire({
                icon: 'success',
                title: 'Longitud Acumulada',
                html: `<b class="text-blue-600">${texto}</b>`
            });
        }
    }

    function finalizarPasoAnalisis() {
        if (!modoAnalisisActual) return;
        window.map.off('click', ejecutarPasoAnalisis);
        window.map.off('dblclick', finalizarPasoAnalisis);
        window.map.getContainer().style.cursor = '';

        if (modoAnalisisActual === 'poligono' && puntosAnalisis.length >= 3) {
            puntosAnalisis.push(puntosAnalisis[0]);
            const coordsLatLon = puntosAnalisis.map(p => [p[1], p[0]]);
            
            L.polygon(coordsLatLon, { color: '#16a34a', fillColor: '#22c55e', fillOpacity: 0.3, weight: 3 }).addTo(capaAnalisisGroup);

            const poly = turf.polygon([puntosAnalisis]);
            const metrosCuadrados = turf.area(poly);
            let textoArea = '';

            if (metrosCuadrados >= 10000) {
                const hectareas = metrosCuadrados / 10000;
                textoArea = `${hectareas.toFixed(2)} hectáreas (${metrosCuadrados.toFixed(1)} m²)`;
            } else {
                textoArea = `${metrosCuadrados.toFixed(1)} metros cuadrados ($m^2$)`;
            }

            Swal.fire({
                title: 'Superficie Calculada',
                html: `<b class="text-lg text-green-600">${textoArea}</b>`,
                icon: 'success'
            });
        }
        modoAnalisisActual = null;
    }

    window.activarMedicionAvanzada = function(tipo) {
        if (!window.map) return;
        asegurarCapaAnalisis();
        capaAnalisisGroup.clearLayers();
        puntosAnalisis = [];
        modoAnalisisActual = tipo;
        window.map.getContainer().style.cursor = 'crosshair';

        const mensaje = tipo === 'linea' 
            ? 'Haz clic en varios puntos para medir la longitud total (Regla). Doble clic para finalizar.' 
            : 'Haz clic para trazar los vértices del polígono y calcular su superficie. Doble clic para cerrar y medir.';

        Swal.fire({
            title: tipo === 'linea' ? 'Medición de Línea (Regla)' : 'Medición de Superficie (Polígono)',
            text: mensaje,
            icon: 'info',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000
        });

        window.map.off('click', ejecutarPasoAnalisis);
        window.map.off('dblclick', finalizarPasoAnalisis);
        window.map.on('click', ejecutarPasoAnalisis);
        window.map.on('dblclick', finalizarPasoAnalisis);
    };

    window.activarVerCoordenadas = function() {
        if (!window.map) return;
        Swal.fire({
            title: 'Modo Ver Coordenadas',
            text: 'Haz clic en cualquier punto del mapa para ver y copiar sus coordenadas exactas.',
            icon: 'info',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3500
        });

        window.map.off('click', mostrarCoordenadasClick);
        window.map.on('click', mostrarCoordenadasClick);
    };

    function mostrarCoordenadasClick(e) {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);

        L.popup()
            .setLatLng(e.latlng)
            .setContent(`<div class="p-1 text-xs"><b>Coordenadas:</b><br>Lat: ${lat}<br>Lng: ${lng}</div>`)
            .openOn(window.map);

        window.map.off('click', mostrarCoordenadasClick);
    }
window.marcarPorCoordenadas = async function(idSimbologiaParam = null) {
        // Obtención segura de idSimbologia evitando ReferenceError
        let idSimbologiaDefecto = null;

        if (typeof idSimbologiaParam !== 'undefined' && idSimbologiaParam !== null && idSimbologiaParam !== '') {
            idSimbologiaDefecto = idSimbologiaParam;
        } else if (typeof idSimbologiaActiva !== 'undefined' && idSimbologiaActiva !== null) {
            idSimbologiaDefecto = idSimbologiaActiva;
        } else if (typeof idSimbologia !== 'undefined' && idSimbologia !== null) {
            idSimbologiaDefecto = idSimbologia;
        } else if (typeof catalogoSimbolos !== 'undefined' && Array.isArray(catalogoSimbolos) && catalogoSimbolos.length > 0) {
            idSimbologiaDefecto = catalogoSimbolos[0].id_simbologia;
        }

        const simboloSeleccionado = (typeof catalogoSimbolos !== 'undefined' && Array.isArray(catalogoSimbolos))
            ? catalogoSimbolos.find(s => s.id_simbologia && s.id_simbologia.toString() === String(idSimbologiaDefecto))
            : null;

        const nombreSimbologia = simboloSeleccionado 
            ? `${simboloSeleccionado.categoria} - ${simboloSeleccionado.nombre_elemento}` 
            : 'Simbología Seleccionada';

        const { value: formValues } = await Swal.fire({
            title: 'Marcar Ubicación por Coordenadas',
            html: `
                <div class="space-y-3 text-left" style="text-align: left; font-size: 0.9em;">
                    <!-- Simbología como Label Fijo e Inmutable -->
                    <div class="mb-3">
                        <label class="text-xs font-semibold text-gray-600 uppercase mb-1" style="display: block;">Simbología Asignada:</label>
                        <div style="background-color: #e9ecef; border: 1px solid #ced4da; padding: 8px 12px; border-radius: 6px; font-weight: 600; color: #343a40;">
                            <i class="fas fa-tag me-1 text-primary"></i> ${nombreSimbologia}
                        </div>
                        <input type="hidden" id="swal-input-simbologia" value="${idSimbologiaDefecto || ''}">
                    </div>

                    <div class="grid grid-cols-2 gap-2 row">
                        <div class="col-6 mb-2">
                            <label class="text-xs font-semibold text-gray-600 uppercase mb-1">Latitud</label>
                            <input id="swal-input-lat" type="number" step="any" placeholder="Ej: 7.5123" class="w-full mt-1 p-2 border rounded text-sm outline-none style-input-reset m-0">
                        </div>
                        <div class="col-6 mb-2">
                            <label class="text-xs font-semibold text-gray-600 uppercase mb-1">Longitud</label>
                            <input id="swal-input-lng" type="number" step="any" placeholder="Ej: -66.0456" class="w-full mt-1 p-2 border rounded text-sm outline-none style-input-reset m-0">
                        </div>
                    </div>

                    <div class="mb-2">
                        <label class="text-xs font-semibold text-gray-600 uppercase mb-1">Nombre / Etiqueta</label>
                        <input id="swal-input-label" type="text" placeholder="Ej: Punto de Control A" class="w-full mt-1 p-2 border rounded text-sm outline-none style-input-reset m-0">
                    </div>

                    <div class="mb-2">
                        <label class="text-xs font-semibold text-gray-600 uppercase mb-1">Descripción</label>
                        <textarea id="swal-input-desc" placeholder="Descripción del elemento..." class="w-full mt-1 p-2 border rounded text-sm outline-none resize-none h-16 style-input-reset m-0" rows="2"></textarea>
                    </div>
                </div>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Ubicar en el Mapa',
            cancelButtonText: 'Cancelar',
            preConfirm: () => {
                const lat = parseFloat(document.getElementById('swal-input-lat').value);
                const lng = parseFloat(document.getElementById('swal-input-lng').value);
                const nombre_propio = document.getElementById('swal-input-label').value.trim() || 'Punto exacto';
                const descripcion = document.getElementById('swal-input-desc').value.trim();
                const id_simbologia = document.getElementById('swal-input-simbologia').value;

                if (isNaN(lat) || isNaN(lng)) {
                    Swal.showValidationMessage('Por favor ingresa valores numéricos válidos para latitud y longitud.');
                    return false;
                }

                const latlng = L.latLng(lat);
                if (typeof capaLayout !== 'undefined' && capaLayout) {
                    const bounds = capaLayout.getBounds();
                    if (!bounds.contains(latlng)) {
                        Swal.showValidationMessage('Error: Las coordenadas se encuentran fuera de los límites del Layout establecido.');
                        return false;
                    }
                }

                return { 
                    lat, 
                    lng, 
                    nombre_propio, 
                    descripcion, 
                    id_simbologia,
                    id_elemento: 'temp_' + Date.now() 
                };
            }
        });

        if (formValues) {
            const tempId = formValues.id_elemento;
            const latlng = [formValues.lat, formValues.lng];
            const geojson = { type: 'Point', coordinates: [formValues.lng, formValues.lat] };
            const simboloCatalogo = (typeof catalogoSimbolos !== 'undefined' && Array.isArray(catalogoSimbolos))
                ? catalogoSimbolos.find(s => s.id_simbologia && s.id_simbologia.toString() === String(formValues.id_simbologia))
                : null;

            const featureGeoJson = {
                "type": "Feature",
                "properties": {
                    "id": tempId,
                    "id_simbologia": formValues.id_simbologia,
                    "nombre_elemento": simboloCatalogo ? simboloCatalogo.nombre_elemento : '',
                    "categoria": simboloCatalogo ? simboloCatalogo.categoria : '',
                    "descripcion": formValues.descripcion,
                    "nombre_propio": formValues.nombre_propio,
                    "estilo_defecto": (simboloCatalogo && typeof parsearEstilo === 'function') ? parsearEstilo(simboloCatalogo.estilo_defecto) : {},
                    "estilo_personalizado": null
                },
                "geometry": geojson
            };

            const tempCapaGroup = L.geoJSON(featureGeoJson, opcionesGeoJson).addTo(map);
            let capaAgregada = null;
            tempCapaGroup.eachLayer(l => capaAgregada = l);

            if (capaAgregada) {
                capaAgregada.featureId = tempId;
                capaAgregada.id_elemento = tempId;
                capaAgregada.id_simbologia = formValues.id_simbologia;
                capaAgregada.nombre_elemento = featureGeoJson.properties.nombre_elemento;
                capaAgregada.nombre_propio = formValues.nombre_propio;
                capaAgregada.descripcion = formValues.descripcion;

                mapaCapas[tempId] = capaAgregada;

                capaAgregada.on('click', function(e) {
                    if (typeof abrirPopupUnico === 'function') {
                        abrirPopupUnico(capaAgregada, featureGeoJson.properties, tempId, e.latlng);
                    }
                });

                map.setView(latlng, 16);
            }

            const datosCreacion = {
                tempId: tempId,
                id_simbologia: formValues.id_simbologia,
                descripcion: formValues.descripcion,
                nombre_propio: formValues.nombre_propio,
                geometria: geojson,
                estiloCustom: null
            };

            estadoCambios.creados.push(datosCreacion);
            historialAcciones.push({ tipo: 'crear_elemento', id: tempId, capa: capaAgregada, datosCreacion: datosCreacion });
            if (typeof actualizarBotonDeshacer === 'function') actualizarBotonDeshacer();
            if (typeof renderizarLeyenda === 'function') renderizarLeyenda();
        }
    };
    window.medirElementoRiesgoExistente = function(id) {
        const capa = mapaCapas[id];
        if (!capa) return Swal.fire('Error', 'Elemento no encontrado en el mapa.', 'error');

        const geojson = capa.toGeoJSON();
        const tipo = geojson.geometry.type;

        if (tipo.includes('Polygon')) {
            const areaM2 = turf.area(geojson);
            const areaHa = areaM2 / 10000;
            Swal.fire({
                title: 'Superficie del Elemento',
                html: `<p>Este polígono de riesgo tiene un área de:</p>
                       <b class="text-blue-600 text-lg">${areaHa.toFixed(2)} hectáreas</b><br>
                       <span class="text-xs text-gray-500">(${areaM2.toFixed(1)} metros cuadrados)</span>`,
                icon: 'info'
            });
        } else if (tipo.includes('Line')) {
            const longitudM = turf.length(geojson, { units: 'meters' });
            const longitudKm = longitudM / 1000;
            Swal.fire({
                title: 'Longitud del Elemento',
                html: `<p>Esta línea o vía de riesgo tiene una longitud de:</p>
                       <b class="text-blue-600 text-lg">${longitudKm.toFixed(2)} km</b><br>
                       <span class="text-xs text-gray-500">(${longitudM.toFixed(1)} metros)</span>`,
                icon: 'info'
            });
        } else if (tipo.includes('Point')) {
            const coords = geojson.geometry.coordinates;
            const lng = coords[0];
            const lat = coords[1];
            Swal.fire({
                title: 'Coordenadas del Marcador',
                html: `<p>Ubicación geográfica exacta:</p>
                       <div class="mt-2 text-sm space-y-1">
                           <div><b>Latitud:</b> <span class="text-blue-600 font-mono">${lat.toFixed(6)}</span></div>
                           <div><b>Longitud:</b> <span class="text-blue-600 font-mono">${lng.toFixed(6)}</span></div>
                       </div>`,
                icon: 'info'
            });
        } else {
            Swal.fire('Aviso', 'Tipo de geometría no compatible para medición.', 'warning');
        }
    };

    window.limpiarMedicion = function() {
        if (capaAnalisisGroup) {
            capaAnalisisGroup.clearLayers();
        }
        modoAnalisisActual = null;
        if (window.map) {
            window.map.getContainer().style.cursor = '';
            window.map.off('click', ejecutarPasoAnalisis);
            window.map.off('dblclick', finalizarPasoAnalisis);
            window.map.off('click', mostrarCoordenadasClick);
        }
        Swal.fire({
            title: 'Análisis Limpiado',
            toast: true, position: 'top-end', icon: 'success', showConfirmButton: false, timer: 1500
        });
    };
function validarBloqueoDeGuardado() {
    const cantidadElementos = Object.keys(mapaCapas).length;
    
    // Si no hay capa layout PERO existen elementos de riesgo (la comunidad no cuenta)
    if (!capaLayout && cantidadElementos > 0) {
        Swal.fire({
            icon: 'error',
            title: 'No se puede guardar',
            text: `Tienes ${cantidadElementos} elemento(s) dibujados en el mapa, pero te falta insertar un Layout (Marco). Debes insertar uno que los encierre o eliminar los elementos para poder guardar.`
        });
        return false; // Bloquea el guardado
    }
    
    return true; // Permite el guardado
}
    async function guardarTodoEnServidor(redirigirA = null) {
        Swal.fire({ title: 'Guardando Cambios...', text: 'Enviando información', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
        let errores = [];
        try {
            let bodyMapa = {};
            if (estadoCambios.comunidad === "ELIMINAR") bodyMapa.geometria_comunidad = null;
            else if (estadoCambios.comunidad) bodyMapa.geometria_comunidad = estadoCambios.comunidad;

            if (estadoCambios.layout === "ELIMINAR") bodyMapa.limites_layout = null;
            else if (estadoCambios.layout) {
                let bounds = estadoCambios.layout;
                bodyMapa.limites_layout = [[bounds.getSouthWest().lat, bounds.getSouthWest().lng], [bounds.getNorthEast().lat, bounds.getNorthEast().lng]];
            }

            if (Object.keys(bodyMapa).length > 0) {
                // 🔴 Aquí consumimos la variable del token
                const res = await fetch(`/geomatica/mapas/${mapaId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.ONCC_CONFIG.csrfToken }, body: JSON.stringify(bodyMapa) });
                if (!res.ok) errores.push("Error guardando límites generales");
            }

            for (let id of estadoCambios.eliminados) { 
                // 🔴 Aquí consumimos la variable del token
                const res = await fetch(`/geomatica/elementos/${id}`, { method: 'DELETE', headers: { 'X-CSRFToken': window.ONCC_CONFIG.csrfToken } }); 
                if (!res.ok) errores.push(`Error borrando elemento: ${id}`); 
            }

            for (let id in estadoCambios.actualizados) { 
                // 🔴 Aquí consumimos la variable del token
                const res = await fetch(`/geomatica/elementos/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.ONCC_CONFIG.csrfToken }, body: JSON.stringify(estadoCambios.actualizados[id]) }); 
                if (!res.ok) errores.push(`Error actualizando: ${id}`); 
            }
            
            for (let elemento of estadoCambios.creados) {
                elemento.id_mapa_riesgo = mapaId;
                // 🔴 Aquí consumimos la variable del token
                const res = await fetch(`/geomatica/crear_mapa`, { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.ONCC_CONFIG.csrfToken }, 
                    body: JSON.stringify(elemento) 
                }); 
                if (!res.ok) errores.push(`Error creando nuevo elemento`);
            }

            if (errores.length === 0) {
                await Swal.fire('¡Éxito!', 'Los cambios han sido guardados correctamente.', 'success');
                if (redirigirA) window.location.href = redirigirA;
                else location.reload();
            } else {
                Swal.fire('Atención', 'Ocurrieron algunos errores al guardar: <br>' + errores.join('<br>'), 'warning');
            }
        } catch (err) {
            console.error(err);
            Swal.fire('Error', 'Error de conexión con el servidor', 'error');
        }
    }

    document.getElementById('btn-guardar').addEventListener('click', () => {
        if (validarBloqueoDeGuardado()) {
            guardarTodoEnServidor();
        }
    });
});