const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const codigo = fs.readFileSync(
    path.join(__dirname, "../static/instrumentos/js/validaciones.js"), "utf8"
);

function iniciar(selector, atributos) {
    const eventos = new Map();
    const aviso = {};
    const contador = { id: "campo_contador" };
    const campo = {
        id: "campo",
        value: "",
        selectionStart: 0,
        selectionEnd: 0,
        setAttribute() {},
        setSelectionRange(posicion) { this.selectionStart = this.selectionEnd = posicion; },
        setCustomValidity(mensaje) { this.error = mensaje; },
        addEventListener(tipo, listener) { eventos.set(tipo, listener); },
        emitir(tipo, detalle = {}) {
            const evento = {
                cancelable: true,
                preventDefault() { this.defaultPrevented = true; },
                ...detalle,
            };
            eventos.get(tipo)(evento);
            return evento.defaultPrevented === true;
        },
        ...atributos,
    };
    const document = {
        querySelectorAll: (busqueda) => busqueda === selector ? [campo] : [],
        getElementById: (id) => id === contador.id ? contador : aviso,
    };
    vm.runInNewContext(codigo, { document });
    return { campo, contador, aviso };
}

test("stock bloquea letras, signos, cuarto dígito y pegados inválidos", () => {
    const { campo, aviso } = iniciar("[data-error-stock]", {
        value: "999", maxLength: 3, selectionStart: 3, selectionEnd: 3,
        pattern: "[0-9]{1,3}",
        dataset: { errorStock: "Stock inválido", maxDigitos: "3" },
    });
    for (const data of ["0", "a", "-"]) {
        assert.ok(campo.emitir("beforeinput", { inputType: "insertText", data }));
        assert.equal(campo.value, "999");
    }
    campo.setSelectionRange(0);
    campo.selectionEnd = 3;
    for (const texto of ["1000", "12a", "+99", "1.5"]) {
        assert.ok(campo.emitir("paste", { clipboardData: { getData: () => texto } }));
        assert.equal(campo.value, "999");
        assert.equal(aviso.textContent, "Stock inválido");
    }
    assert.ok(campo.emitir("paste", { clipboardData: { getData: () => "123" } }));
    assert.equal(campo.value, "123");
    assert.equal(aviso.hidden, true);
    campo.value = "12a";
    campo.emitir("input");
    assert.equal(campo.value, "123");
    campo.value = "1234";
    campo.emitir("input");
    assert.equal(campo.value, "123");
    campo.value = "";
    campo.emitir("input", { inputType: "deleteContentBackward" });
    assert.equal(campo.value, "");
});

test("el contador conserva maxlength y refleja el límite de descripción", () => {
    const { campo, contador } = iniciar("[data-contador]", {
        value: "a".repeat(100), maxLength: 100, dataset: { contador: "100" },
    });
    assert.equal(campo.maxLength, 100);
    assert.equal(contador.textContent, "100 / 100 caracteres");
    campo.value += "a";
    campo.emitir("input");
    assert.match(campo.error, /100 caracteres/);
});

function iniciarPrecio() {
    return iniciar("[data-precio-clp]", {
        pattern: "\\$?(?:[0-9]{1,6}|[0-9]{1,3}\\.[0-9]{3})",
        dataset: { errorPrecio: "Precio inválido", maxDigitos: "6" },
    });
}

test("precio formatea la escritura y bloquea letras, signos y séptimo dígito", () => {
    const { campo, aviso } = iniciarPrecio();
    for (const data of "100000") {
        assert.ok(campo.emitir("beforeinput", { inputType: "insertText", data }));
    }
    assert.equal(campo.value, "$100.000");
    for (const data of ["1", "a", "-", ".", ","]) {
        assert.ok(campo.emitir("beforeinput", { inputType: "insertText", data }));
        assert.equal(campo.value, "$100.000");
        assert.equal(aviso.textContent, "Precio inválido");
    }
    campo.setSelectionRange(5);
    campo.emitir("beforeinput", { inputType: "deleteContentBackward" });
    assert.equal(campo.value, "$10.000");
    campo.setSelectionRange(0);
    campo.selectionEnd = campo.value.length;
    campo.emitir("beforeinput", { inputType: "insertText", data: "1" });
    assert.equal(campo.value, "$1");
    campo.emitir("beforeinput", { inputType: "deleteContentBackward" });
    assert.equal(campo.value, "");
});

test("precio rechaza pegado, arrastre y entradas inválidas sin cambiar el último valor", () => {
    const { campo } = iniciarPrecio();
    const transferencia = (texto) => ({ getData: () => texto });
    campo.emitir("paste", { clipboardData: transferencia("$999.999") });
    assert.equal(campo.value, "$999.999");
    campo.setSelectionRange(0);
    campo.selectionEnd = campo.value.length;
    for (const texto of ["1000000", "$1.00.0", "1.50", "abc", "-55"]) {
        assert.ok(campo.emitir("paste", { clipboardData: transferencia(texto) }));
        assert.ok(campo.emitir("drop", { dataTransfer: transferencia(texto) }));
        assert.equal(campo.value, "$999.999");
    }
    campo.emitir("drop", { dataTransfer: transferencia("100000") });
    assert.equal(campo.value, "$100.000");
    campo.value = "$100.000a";
    campo.emitir("input", { inputType: "insertText" });
    assert.equal(campo.value, "$100.000");
    campo.emitir("beforeinput", { inputType: "insertText", data: "1", cancelable: false });
    campo.value = "$100.0001";
    campo.emitir("input", { inputType: "insertText" });
    assert.equal(campo.value, "$100.000");
});
