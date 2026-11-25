for (const panel of document.querySelectorAll(".recepcion-menu, .recepcion-panel")) {
    const botones = document.querySelectorAll(`[data-recepcion-dialogo][aria-controls="${panel.id}"]`);
    let origen = null;

    for (const boton of botones) {
        boton.addEventListener("click", () => {
            if (panel.open) return;
            panel.showModal();
            origen = boton;
            boton.setAttribute("aria-expanded", "true");
        });
    }

    panel.addEventListener("close", () => {
        origen?.setAttribute("aria-expanded", "false");
        origen?.focus();
        origen = null;
    });

    panel.addEventListener("click", (evento) => {
        if (evento.target.closest("a[href]")) {
            panel.close();
        } else if (evento.target === panel) {
            const { left, top, right, bottom } = panel.getBoundingClientRect();
            if (evento.clientX < left || evento.clientX > right
                || evento.clientY < top || evento.clientY > bottom) {
                panel.close();
            }
        }
    });
}
