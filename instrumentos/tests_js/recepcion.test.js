const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const codigo = fs.readFileSync(
    path.join(__dirname, "../static/instrumentos/js/recepcion.js"), "utf8"
);

function crearBoton(eventos) {
    return {
        "aria-expanded": "false",
        addEventListener(tipo, fn) { eventos.abrir = fn; },
        setAttribute(nombre, valor) { this[nombre] = valor; },
        focus() { this.enfocado = true; },
    };
}

function crearPanel(id) {
    const eventos = {};
    const boton = crearBoton(eventos);
    const menu = {
        id,
        open: false,
        addEventListener(tipo, fn) { eventos[tipo] = fn; },
        showModal() { this.open = true; },
        close() { this.open = false; eventos.close(); },
        closest() { return null; },
        getBoundingClientRect: () => ({ left: 0, right: 300, top: 0, bottom: 600 }),
    };
    return { eventos, boton, menu };
}

function iniciar() {
    const paneles = Object.fromEntries(
        ["menu-recepcion", "menu-computador", "menu-historia"].map((id) => [id, crearPanel(id)])
    );
    const accionesLetrero = {};
    const letrero = crearBoton(accionesLetrero);
    vm.runInNewContext(codigo, { document: {
        querySelectorAll(selector) {
            if (selector === ".recepcion-menu, .recepcion-panel") {
                return Object.values(paneles).map(({ menu }) => menu);
            }
            const id = selector.match(/aria-controls="([^"]+)"/)[1];
            return id === "menu-historia" ? [paneles[id].boton, letrero] : [paneles[id].boton];
        },
    } });
    return { paneles, letrero, accionesLetrero };
}

test("el botón abre un diálogo y el cierre nativo devuelve el foco", () => {
    const { paneles } = iniciar();
    for (const { eventos, boton, menu } of Object.values(paneles)) {
        eventos.abrir({ detail: 0 });
        assert.equal(menu.open, true);
        assert.equal(boton["aria-expanded"], "true");
        // El navegador cierra dialog al pulsar Escape y emite close.
        menu.close();
        assert.equal(boton["aria-expanded"], "false");
        assert.equal(boton.enfocado, true);
    }
});

test("el panel se cierra al seleccionar un enlace o pulsar el fondo", () => {
    const { paneles } = iniciar();
    const { eventos, menu } = paneles["menu-computador"];
    eventos.abrir();
    eventos.click({ target: menu, clientX: 150, clientY: 100 });
    assert.equal(menu.open, true);
    eventos.click({ target: menu, clientX: 500, clientY: 100 });
    assert.equal(menu.open, false);
    eventos.abrir();
    eventos.click({ target: { closest: () => ({ href: "/instrumentos/" }) } });
    assert.equal(menu.open, false);
});

test("el letrero y el botón abren el mismo panel y recuperan su propio foco", () => {
    const { paneles, letrero, accionesLetrero } = iniciar();
    const { eventos, menu, boton } = paneles["menu-historia"];
    accionesLetrero.abrir({ detail: 0 });
    assert.equal(menu.open, true);
    assert.equal(letrero["aria-expanded"], "true");
    assert.equal(boton["aria-expanded"], "false");
    menu.close();
    assert.equal(letrero["aria-expanded"], "false");
    assert.equal(letrero.enfocado, true);
    assert.equal(boton.enfocado, undefined);
    letrero.enfocado = false;
    eventos.abrir({ pointerType: "touch" });
    assert.equal(menu.open, true);
    menu.close();
    assert.equal(boton.enfocado, true);
    assert.equal(letrero.enfocado, false);
});

test("las transiciones de recepción respetan movimiento reducido", () => {
    const css = fs.readFileSync(path.join(__dirname, "../static/instrumentos/css/recepcion.css"), "utf8");
    assert.match(css, /@media \(prefers-reduced-motion: reduce\)\s*\{[\s\S]*?transition: none/);
});
