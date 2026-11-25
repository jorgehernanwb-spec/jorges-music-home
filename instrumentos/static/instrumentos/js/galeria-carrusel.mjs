import {iniciarVisor} from "./galeria-visor.mjs";

export function siguienteIndice(indice, paso, total) {
    return (indice + paso + total) % total;
}

const cuadros = (origen, destino) => [origen, destino].map(([x, opacity]) => ({
    transform: `translateX(${x}%)`,
    opacity,
}));

export function iniciarCarrusel(sala, entorno = window, prepararVisor = iniciarVisor) {
    const fichas = [...sala.querySelectorAll("[data-acabado]")];
    const posicion = sala.querySelector("[data-posicion]");
    const escena = sala.querySelector("[data-escena]");
    const modelo = sala.querySelector("[data-modelo]");
    const acciones = sala.querySelector("[data-acciones]");
    const dialogo = sala.querySelector("[data-dialogo]");
    const ficha = sala.querySelector("[data-ficha]");
    const abrir = sala.querySelector("[data-especificaciones]");
    const movimientoReducido = entorno.matchMedia("(prefers-reduced-motion: reduce)");
    let indice = Number(sala.dataset.indice) || 0;
    let transicion = null;
    let cambiando = false;

    if (!fichas.length || typeof dialogo.showModal !== "function") return;

    escena.hidden = acciones.hidden = posicion.hidden = false;
    const visor = prepararVisor(sala, entorno, fichas[indice].dataset.acabado, sala.dataset.categoria);
    sala.querySelector("[data-fichas]").hidden = true;

    function actualizar() {
        const pieza = fichas[indice];
        posicion.textContent = `${indice + 1} de ${fichas.length} · ${pieza.dataset.identidad}`;
        ficha.replaceChildren(pieza.querySelector("article").cloneNode(true));
    }

    async function deslizar(origen, destino, duracion) {
        if (!visor || movimientoReducido.matches || !modelo.animate || modelo.querySelector("canvas").hidden) return;
        transicion = modelo.animate(cuadros(origen, destino),
            {duration: duracion, easing: "ease-in-out", fill: "both"});
        try {
            await transicion.finished;
        } catch {
            // Cancelar el movimiento conserva el cambio de instrumento.
        }
    }

    async function cambiar(paso) {
        if (cambiando) return;
        cambiando = true;
        abrir.disabled = true;
        try {
            await deslizar([0, 1], [-paso * 45, 0], 180);
            indice = siguienteIndice(indice, paso, fichas.length);
            if (visor) visor.seleccionar(fichas[indice].dataset.acabado);
            actualizar();
            const salida = transicion;
            const entrada = deslizar([paso * 45, 0], [0, 1], 260);
            salida?.cancel();
            await entrada;
        } finally {
            transicion?.cancel();
            transicion = null;
            abrir.disabled = false;
            cambiando = false;
        }
    }

    for (const flecha of sala.querySelectorAll("[data-paso]")) {
        flecha.hidden = fichas.length < 2;
        if (!flecha.hidden) flecha.addEventListener("click", () => cambiar(Number(flecha.dataset.paso)));
    }
    movimientoReducido.addEventListener("change", () => {
        if (movimientoReducido.matches) transicion?.cancel();
    });
    abrir.addEventListener("click", () => dialogo.showModal());
    let pulsacionFuera = false;
    const fuera = (evento) => {
        const {left, right, top, bottom} = dialogo.getBoundingClientRect();
        return evento.target === dialogo && (
            evento.clientX < left || evento.clientX >= right || evento.clientY < top || evento.clientY >= bottom
        );
    };
    dialogo.addEventListener("pointerdown", (evento) => { pulsacionFuera = fuera(evento); });
    dialogo.addEventListener("click", (evento) => {
        if (pulsacionFuera && fuera(evento)) dialogo.close();
        pulsacionFuera = false;
    });
    dialogo.addEventListener("close", () => abrir.focus());
    actualizar();
}

if (typeof document !== "undefined") {
    const sala = document.querySelector("[data-carrusel]");
    if (sala) iniciarCarrusel(sala);
}
