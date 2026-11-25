const escena = document.querySelector(".fachada-escena");
const entrada = escena.querySelector(".fachada-puertas");
const movimientoReducido = window.matchMedia("(prefers-reduced-motion: reduce)");
let temporizador = null;

entrada.addEventListener("click", (evento) => {
    if (evento.defaultPrevented || evento.button !== 0 || evento.ctrlKey
        || evento.metaKey || evento.shiftKey || evento.altKey || movimientoReducido.matches) {
        return;
    }

    evento.preventDefault();
    if (temporizador !== null) return;

    escena.classList.add("esta-entrando");
    // 480 ms de apertura y 450 ms con el interior a la vista.
    temporizador = window.setTimeout(() => window.location.assign(entrada.href), 930);
});

window.addEventListener("pageshow", () => {
    window.clearTimeout(temporizador);
    temporizador = null;
    escena.classList.remove("esta-entrando");
});
