import {crearRenderizador} from "./galeria-glb.mjs";
import {modelos} from "./modelos-glb.mjs";

export function iniciarVisor(pagina, entorno = window, acabado = "", categoria = "guitarras") {
    const canvas = pagina.querySelector("[data-visor]");
    const alternativo = pagina.querySelector("[data-visor-alternativo]");
    const controles = pagina.querySelector("[data-visor-controles]");
    const nota = pagina.querySelector("[data-visor-nota]");
    const botonFlotacion = pagina.querySelector("[data-flotacion]");
    const movimientoReducido = entorno.matchMedia("(prefers-reduced-motion: reduce)");
    const modelo = modelos[categoria];
    const orientacionInicial = modelo?.orientacion ?? [0, 0];
    let [horizontal, vertical] = orientacionInicial;
    let color = acabado;
    let pausa = false;
    let animacion = 0;
    let puntero = null;
    let renderizador;
    let observador;

    function detener() {
        entorno.cancelAnimationFrame(animacion);
        movimientoReducido.removeEventListener?.("change", actualizarFlotacion);
        observador?.disconnect();
        renderizador?.cerrar();
    }

    function mostrarAlternativa() {
        detener();
        const activo = canvas.ownerDocument?.activeElement;
        const recuperarFoco = activo === canvas || controles.contains(activo);
        canvas.hidden = controles.hidden = true;
        if (nota) nota.hidden = true;
        alternativo.textContent = "Visor 3D no disponible. Puedes consultar las especificaciones.";
        alternativo.hidden = false;
        if (recuperarFoco) {
            alternativo.tabIndex = -1;
            alternativo.focus();
        }
    }

    function flota() {
        return !pausa && !movimientoReducido.matches;
    }

    function dibujar(tiempo = 0) {
        if (!canvas.hidden) {
            renderizador.render(horizontal, vertical, flota() ? Math.sin(tiempo / 1100) * .032 : 0, color);
        }
    }

    function animar(tiempo) {
        dibujar(tiempo);
        animacion = entorno.requestAnimationFrame(animar);
    }

    function actualizarFlotacion() {
        entorno.cancelAnimationFrame(animacion);
        botonFlotacion.hidden = movimientoReducido.matches;
        botonFlotacion.setAttribute("aria-pressed", String(pausa));
        if (!canvas.hidden && flota()) animacion = entorno.requestAnimationFrame(animar);
        else dibujar();
    }

    function girar(x, y = 0) {
        horizontal = (horizontal + x) % (2 * Math.PI);
        vertical = Math.max(-.85, Math.min(.85, vertical + y));
        if (!flota()) dibujar();
    }

    try {
        if (!modelo) throw new Error("Modelo no disponible");
        renderizador = crearRenderizador(canvas, modelo);
    } catch {
        mostrarAlternativa();
        return false;
    }

    alternativo.textContent = "Cargando el modelo 3D…";
    renderizador.listo.then((cargado) => {
        if (!cargado) return;
        canvas.hidden = controles.hidden = false;
        if (nota) nota.hidden = false;
        dibujar();
        alternativo.hidden = true;
        observador = new entorno.ResizeObserver(() => { if (!flota()) dibujar(); });
        observador.observe(canvas);
        movimientoReducido.addEventListener("change", actualizarFlotacion);
        actualizarFlotacion();
    }).catch(mostrarAlternativa);

    canvas.addEventListener("webglcontextlost", mostrarAlternativa);
    entorno.addEventListener("pagehide", (evento) => { if (!evento.persisted) detener(); });
    canvas.addEventListener("pointerdown", (evento) => {
        if (!evento.isPrimary || evento.button !== 0) return;
        canvas.setPointerCapture(evento.pointerId);
        puntero = evento;
    });
    canvas.addEventListener("pointermove", (evento) => {
        if (puntero?.pointerId !== evento.pointerId) return;
        girar((evento.clientX - puntero.clientX) * .013, (evento.clientY - puntero.clientY) * .009);
        puntero = evento;
    });
    canvas.addEventListener("lostpointercapture", () => { puntero = null; });
    canvas.addEventListener("keydown", (evento) => {
        const giros = {
            ArrowLeft: [-.2, 0], ArrowRight: [.2, 0], ArrowUp: [0, -.15], ArrowDown: [0, .15],
        };
        if (!Object.hasOwn(giros, evento.key)) return;
        evento.preventDefault();
        girar(...giros[evento.key]);
    });
    function centrar() {
        [horizontal, vertical] = orientacionInicial;
        if (!flota()) dibujar();
    }
    pagina.querySelector("[data-centrar]").addEventListener("click", centrar);
    botonFlotacion.addEventListener("click", () => {
        pausa = !pausa;
        actualizarFlotacion();
    });
    return {
        seleccionar(acabado) {
            color = acabado;
            centrar();
        },
    };
}
