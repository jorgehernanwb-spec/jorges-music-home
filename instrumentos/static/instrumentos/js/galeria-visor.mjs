import {crearRenderizador} from "./galeria-webgl.mjs";
import {modelos} from "./modelos-galeria.mjs";
const acabadoInicial = [.73, .29, .13];

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
    let color = colorDelAcabado(acabado);
    let pausa = false;
    let animacion = 0;
    let puntero = null;
    let renderizar;

    function mostrarAlternativa() {
        entorno.cancelAnimationFrame(animacion);
        animacion = 0;
        const activo = canvas.ownerDocument?.activeElement;
        const recuperarFoco = activo === canvas || controles.contains(activo);
        canvas.hidden = controles.hidden = true;
        if (nota) nota.hidden = true;
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
            renderizar(horizontal, vertical, flota() ? Math.sin(tiempo / 1100) * .045 : 0, color);
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
        renderizar = crearRenderizador(canvas, modelo);
        canvas.hidden = controles.hidden = false;
        if (nota) nota.hidden = false;
        dibujar();
        alternativo.hidden = true;
    } catch {
        mostrarAlternativa();
        return false;
    }

    canvas.addEventListener("webglcontextlost", mostrarAlternativa);
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
    movimientoReducido.addEventListener("change", actualizarFlotacion);
    new entorno.ResizeObserver(() => { if (!flota()) dibujar(); }).observe(canvas);
    actualizarFlotacion();
    return {
        seleccionar(acabado) {
            color = colorDelAcabado(acabado);
            centrar();
        },
    };
}

export function colorDelAcabado(hex) {
    return /^#[\da-f]{6}$/i.test(hex)
        ? hex.slice(1).match(/../g).map((canal) => parseInt(canal, 16) / 255)
        : acabadoInicial;
}
