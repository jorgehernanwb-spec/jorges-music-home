const assert = require("node:assert/strict");
const test = require("node:test");

test("el modelo original contiene triángulos, volumen, normales y piezas con acabado", async () => {
    const {geometriaGuitarra} = await import("../static/instrumentos/js/guitarra-geometria.mjs");
    const malla = geometriaGuitarra();
    assert.equal(malla.length % 30, 0);
    assert.ok(malla.length > 30);
    let frente = 0, fondo = 0, cuerpo = 0, piezas = 0;
    const bordesDeCuerdas = new Set();
    for (let i = 0; i < malla.length; i += 10) {
        assert.ok(malla.slice(i, i + 10).every(Number.isFinite));
        assert.ok(Math.abs(Math.hypot(...malla.slice(i + 3, i + 6)) - 1) < .0001);
        frente = Math.max(frente, malla[i + 2]);
        fondo = Math.min(fondo, malla[i + 2]);
        if (malla[i + 9]) cuerpo++;
        else piezas++;
        if (Math.abs(malla[i + 1] - 1.14) < .0001 && Math.abs(malla[i + 2] - .187) < .0001) {
            bordesDeCuerdas.add(malla[i]);
        }
    }
    assert.ok(frente > .12 && fondo < -.12 && cuerpo > 0 && piezas > 0);
    assert.equal(bordesDeCuerdas.size, 12);
});

test("sin WebGL se mantienen el aviso accesible y los controles ocultos", async () => {
    const {iniciarVisor} = await import("../static/instrumentos/js/galeria-visor.mjs");
    const aviso = {hidden: false};
    const canvas = {hidden: true, getContext: () => null};
    const controles = {hidden: true, contains: () => false};
    const elementos = new Map([
        ["[data-visor]", canvas], ["[data-visor-alternativo]", aviso],
        ["[data-visor-controles]", controles],
    ]);
    const pagina = {activeElement: {}, querySelector: (selector) => elementos.get(selector) ?? null};
    const entorno = {matchMedia: () => ({matches: true}), cancelAnimationFrame: () => {}};
    assert.equal(iniciarVisor(pagina, entorno), false);
    assert.equal(aviso.hidden, false);
    assert.equal(canvas.hidden, true);
    assert.equal(controles.hidden, true);
});

test("el visor convierte el acabado del registro a canales WebGL", async () => {
    const {colorDelAcabado} = await import("../static/instrumentos/js/galeria-visor.mjs");
    assert.deepEqual(colorDelAcabado("#CF3434"), [207 / 255, 52 / 255, 52 / 255]);
    assert.deepEqual(colorDelAcabado("#F1F0E9"), [241 / 255, 240 / 255, 233 / 255]);
    assert.deepEqual(colorDelAcabado(""), [.73, .29, .13]);
});

test("las cuatro salas tienen mallas volumétricas distintas con acabado parcial", async () => {
    const {modelos} = await import("../static/instrumentos/js/modelos-galeria.mjs");
    assert.deepEqual(Object.keys(modelos), ["guitarras", "bajos", "teclados", "baterias"]);
    const tamaños = new Set();
    for (const {malla} of Object.values(modelos)) {
        const datos = malla();
        assert.equal(datos.length % 30, 0);
        assert.ok(datos.every(Number.isFinite));
        tamaños.add(datos.length);
        const acabados = new Set(), profundidades = new Set();
        for (let i = 0; i < datos.length; i += 10) {
            profundidades.add(datos[i + 2]);
            acabados.add(datos[i + 9]);
        }
        assert.ok(profundidades.size > 5);
        assert.deepEqual(acabados, new Set([0, 1]));
    }
    assert.equal(tamaños.size, 4);
});
