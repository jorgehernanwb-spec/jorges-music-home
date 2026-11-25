const assert = require("node:assert/strict");
const test = require("node:test");

function elemento(atributos = {}) {
    const eventos = new Map();
    return {
        hidden: true,
        addEventListener: (tipo, accion) => eventos.set(tipo, accion),
        emitir: (tipo, datos) => eventos.get(tipo)?.(datos),
        ...atributos,
    };
}

function escenario(nombres, reduce = false, indice = "0") {
    const [posicion, escena, acciones, lista] = Array.from({length: 4}, () => elemento());
    const ficha = elemento({replaceChildren(valor) { this.texto = valor; }});
    const abrir = elemento({focus() { this.enfocado = true; }});
    const dialogo = elemento({
        showModal() { this.abierto = true; },
        close() { this.abierto = false; this.emitir("close"); },
        getBoundingClientRect: () => ({left: 10, right: 100, top: 10, bottom: 100}),
    });
    const animaciones = [];
    const modelo = elemento({
        querySelector: () => ({hidden: false}),
        animate(cuadros) {
            animaciones.push(cuadros);
            return {finished: Promise.resolve(), cancel() {}};
        },
    });
    const flechas = [-1, 1].map((paso) => elemento({dataset: {paso}}));
    const colores = nombres.map((_, i) => `#00000${i}`);
    const piezas = nombres.map((nombre, i) => ({
        dataset: {acabado: colores[i], identidad: nombre},
        querySelector: () => ({cloneNode: () => nombre}),
    }));
    const elementos = new Map([
        ["[data-posicion]", posicion], ["[data-escena]", escena], ["[data-modelo]", modelo],
        ["[data-acciones]", acciones], ["[data-dialogo]", dialogo], ["[data-ficha]", ficha],
        ["[data-especificaciones]", abrir], ["[data-fichas]", lista],
    ]);
    const sala = {
        dataset: {categoria: "guitarras", indice},
        querySelector: (selector) => elementos.get(selector),
        querySelectorAll: (selector) => selector === "[data-acabado]" ? piezas : flechas,
    };
    const entorno = {matchMedia: () => elemento({matches: reduce})};
    const aplicados = [];
    const visor = (_, __, color) => {
        aplicados.push(color);
        return {seleccionar: (siguiente) => aplicados.push(siguiente)};
    };
    return {sala, entorno, visor, flechas, posicion, ficha, abrir, dialogo, aplicados, colores, animaciones};
}

test("el carrusel envuelve todos los registros, desliza y sincroniza las especificaciones", async () => {
    const {iniciarCarrusel} = await import("../static/instrumentos/js/galeria-carrusel.mjs");
    const e = escenario(["Pacifica", "RG GIO", "Stratocaster", "Les Paul", "Quinta guitarra"]);
    iniciarCarrusel(e.sala, e.entorno, e.visor);
    assert.equal(e.posicion.textContent, "1 de 5 · Pacifica");
    assert.equal(e.ficha.texto, "Pacifica");
    await e.flechas[0].emitir("click");
    assert.equal(e.posicion.textContent, "5 de 5 · Quinta guitarra");
    assert.equal(e.ficha.texto, "Quinta guitarra");
    assert.deepEqual(e.aplicados, [e.colores[0], e.colores[4]]);
    assert.deepEqual(e.animaciones.map((cuadros) => cuadros.map((cuadro) => cuadro.transform)), [
        ["translateX(0%)", "translateX(45%)"], ["translateX(-45%)", "translateX(0%)"],
    ]);
    await e.flechas[1].emitir("click");
    assert.equal(e.posicion.textContent, "1 de 5 · Pacifica");
});

test("movimiento reducido conserva el cambio y cerrar el diálogo devuelve el foco", async () => {
    const {iniciarCarrusel} = await import("../static/instrumentos/js/galeria-carrusel.mjs");
    const e = escenario(["Pacifica", "Les Paul"], true);
    iniciarCarrusel(e.sala, e.entorno, e.visor);
    await e.flechas[1].emitir("click");
    assert.equal(e.animaciones.length, 0);
    e.abrir.emitir("click");
    assert.equal(e.dialogo.abierto, true);
    assert.equal(e.ficha.texto, "Les Paul");
    const dentro = {target: e.dialogo, clientX: 20, clientY: 20};
    const fuera = {target: e.dialogo, clientX: 2, clientY: 2};
    e.dialogo.emitir("pointerdown", dentro);
    e.dialogo.emitir("click", fuera);
    assert.equal(e.dialogo.abierto, true);
    e.dialogo.emitir("pointerdown", fuera);
    e.dialogo.emitir("click", fuera);
    assert.equal(e.dialogo.abierto, false);
    assert.equal(e.abrir.enfocado, true);
    assert.equal(e.aplicados.length, 2);
});

test("un instrumento mantiene la ficha sin mostrar flechas", async () => {
    const {iniciarCarrusel} = await import("../static/instrumentos/js/galeria-carrusel.mjs");
    const e = escenario(["Pacifica"]);
    iniciarCarrusel(e.sala, e.entorno, e.visor);
    assert.equal(e.posicion.textContent, "1 de 1 · Pacifica");
    assert.ok(e.flechas.every((flecha) => flecha.hidden));
    assert.equal(e.ficha.texto, "Pacifica");
});

test("sin WebGL las flechas conservan el acceso a todas las especificaciones", async () => {
    const {iniciarCarrusel} = await import("../static/instrumentos/js/galeria-carrusel.mjs");
    const e = escenario(["Pacifica", "Les Paul"]);
    iniciarCarrusel(e.sala, e.entorno, () => false);
    await e.flechas[1].emitir("click");
    assert.equal(e.posicion.textContent, "2 de 2 · Les Paul");
    assert.equal(e.ficha.texto, "Les Paul");
    assert.equal(e.animaciones.length, 0);
});

test("la selección directa inicia el visor y las especificaciones en el registro solicitado", async () => {
    const {iniciarCarrusel} = await import("../static/instrumentos/js/galeria-carrusel.mjs");
    const e = escenario(["Pacifica", "Les Paul · Sin stock", "Stratocaster"], true, "1");
    iniciarCarrusel(e.sala, e.entorno, e.visor);
    assert.equal(e.posicion.textContent, "2 de 3 · Les Paul · Sin stock");
    assert.equal(e.ficha.texto, "Les Paul · Sin stock");
    assert.deepEqual(e.aplicados, [e.colores[1]]);
    await e.flechas[1].emitir("click");
    assert.equal(e.posicion.textContent, "3 de 3 · Stratocaster");
});
