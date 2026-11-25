const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const codigo = fs.readFileSync(
    path.join(__dirname, "../static/instrumentos/js/fachada.js"), "utf8"
);

function iniciar(reduced = false) {
    let click, pageshow, pendiente;
    const clases = new Set();
    const destinos = [];
    const enlace = {
        href: "/recepcion/",
        addEventListener(tipo, fn) { click = fn; },
    };
    const escena = {
        querySelector: () => enlace,
        classList: { add: (clase) => clases.add(clase), remove: (clase) => clases.delete(clase) },
    };
    const window = {
        matchMedia: () => ({ matches: reduced }),
        setTimeout(fn, espera) { pendiente = { fn, espera }; return 1; },
        clearTimeout() { pendiente = undefined; },
        location: { assign: (url) => destinos.push(url) },
        addEventListener(tipo, fn) { pageshow = fn; },
    };
    vm.runInNewContext(codigo, { window, document: { querySelector: () => escena } });
    return {
        activar(detail = {}) {
            const evento = {
                button: 0, preventDefault() { this.prevented = true; }, ...detail,
            };
            click(evento);
            return Boolean(evento.prevented);
        },
        clases, destinos,
        programado: () => pendiente,
        restaurar: () => pageshow(),
    };
}

test("la activación por teclado usa la transición y abre la recepción", () => {
    const demo = iniciar();
    assert.equal(demo.activar({ detail: 0 }), true);
    assert.ok(demo.clases.has("esta-entrando"));
    assert.equal(demo.programado().espera, 930);
    demo.programado().fn();
    assert.deepEqual(demo.destinos, ["/recepcion/"]);
    demo.restaurar();
    assert.equal(demo.clases.size, 0);
    assert.equal(demo.programado(), undefined);
});

test("movimiento reducido y clic modificado conservan la navegación nativa", () => {
    assert.equal(iniciar(true).activar(), false);
    const demo = iniciar();
    assert.equal(demo.activar({ ctrlKey: true }), false);
    assert.equal(demo.activar({ button: 1 }), false);
    assert.equal(demo.programado(), undefined);
});
