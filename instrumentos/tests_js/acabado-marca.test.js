const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const codigo = fs.readFileSync(
    path.join(__dirname, "../static/instrumentos/js/acabado-marca.js"), "utf8"
);

test("cambiar la marca actualiza la muestra sin editar el precio", () => {
    let cambiar;
    const estilos = new Map();
    const marca = {
        value: "Fender",
        addEventListener(tipo, listener) {
            assert.equal(tipo, "change");
            cambiar = listener;
        },
    };
    const acabado = {
        hidden: false,
        querySelector: () => ({
            style: {
                setProperty: (propiedad, valor) => estilos.set(propiedad, valor),
                removeProperty: (propiedad) => estilos.delete(propiedad),
            },
        }),
    };
    const elementos = {
        id_marca: marca,
        "acabado-marca": acabado,
        "colores-marca": { textContent: '{"Fender":"#CF3434","Yamaha":"#232323","Roland":"#F1F0E9"}' },
    };
    vm.runInNewContext(codigo, { document: {
        getElementById(id) {
            assert.ok(id in elementos, "El acabado solo interactúa con los controles de marca");
            return elementos[id];
        },
    } });
    for (const [seleccion, color] of [["Yamaha", "#232323"], ["Roland", "#F1F0E9"]]) {
        marca.value = seleccion;
        cambiar();
        assert.equal(acabado.hidden, false);
        assert.equal(estilos.get("--acabado"), color);
    }
    marca.value = "";
    cambiar();
    assert.equal(acabado.hidden, true);
    assert.equal(estilos.has("--acabado"), false);
});
