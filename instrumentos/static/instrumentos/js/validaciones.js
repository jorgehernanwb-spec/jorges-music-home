function mostrarError(campo, mensaje, bloquearEnvio = true) {
    const aviso = document.getElementById(`${campo.id}_aviso`);
    campo.setCustomValidity(bloquearEnvio ? mensaje : "");
    aviso.textContent = mensaje;
    aviso.hidden = !mensaje;
}

function digitos(texto) {
    return texto.replace(/[^0-9]/g, "");
}

function activarNumero(campo, moneda) {
    const maximo = Number(campo.dataset.maxDigitos);
    const mensaje = moneda ? campo.dataset.errorPrecio : campo.dataset.errorStock;
    const formato = new RegExp(`^(?:${campo.pattern})(?![\\s\\S])`);
    let ultimo = "";
    let pendiente = null;

    function leer(texto) {
        if (!texto) return "";
        const entrada = moneda ? texto.trim() : texto;
        return formato.test(entrada) ? digitos(entrada) : null;
    }

    function valido(cifras) {
        return cifras !== null && cifras.length <= maximo
            && (!moneda || !cifras || Number(cifras) > 0);
    }

    function guardar(cifras, restantes) {
        ultimo = moneda && cifras
            ? "$" + String(Number(cifras)).replace(/\B(?=(\d{3})+(?!\d))/g, ".")
            : cifras;
        if (campo.value !== ultimo) {
            campo.value = ultimo;
            let cursor = ultimo.length;
            const inicio = moneda && ultimo ? 1 : 0;
            while (cursor > inicio && digitos(ultimo.slice(cursor)).length < restantes) {
                cursor -= 1;
            }
            campo.setSelectionRange(cursor, cursor);
        }
        mostrarError(campo, "");
    }

    function rechazar(seleccion) {
        if (campo.value !== ultimo) {
            campo.value = ultimo;
            campo.setSelectionRange(...seleccion);
        }
        mostrarError(campo, mensaje, false);
    }

    function reemplazo(texto, tipo) {
        const seleccion = [campo.selectionStart, campo.selectionEnd];
        const [inicio, fin] = seleccion.map((indice) => digitos(ultimo.slice(0, indice)).length);
        const cifras = digitos(ultimo);
        let desde = inicio;
        let hasta = fin;
        let nuevas = texto;
        const borrar = tipo.startsWith("delete");
        if (borrar) {
            nuevas = "";
            if (seleccion[0] === seleccion[1]) {
                if (tipo === "deleteContentBackward") desde = Math.max(0, inicio - 1);
                if (tipo === "deleteContentForward") hasta = Math.min(cifras.length, fin + 1);
            }
        }
        if (nuevas === null) return { cifras: null, seleccion };
        const resultado = cifras.slice(0, desde) + nuevas + cifras.slice(hasta);
        return {
            cifras: borrar && moneda && !Number(resultado) ? "" : resultado,
            restantes: cifras.length - hasta,
            seleccion,
        };
    }

    function aplicar(cambio) {
        if (valido(cambio.cifras)) guardar(cambio.cifras, cambio.restantes);
        else rechazar(cambio.seleccion);
    }

    const inicial = leer(campo.value);
    if (valido(inicial)) guardar(inicial, 0);
    else rechazar([0, 0]);

    campo.addEventListener("beforeinput", (evento) => {
        pendiente = null;
        const tipo = evento.inputType || "";
        const borrar = moneda && ["deleteContentBackward", "deleteContentForward", "deleteByCut"].includes(tipo);
        if (!borrar && !tipo.startsWith("insert")) return;
        const texto = evento.dataTransfer?.getData("text/plain") ?? evento.data;
        if (!borrar && texto == null) return;
        const externas = ["insertFromPaste", "insertFromDrop", "insertReplacementText"].includes(tipo);
        let entrada = "";
        if (!borrar) {
            entrada = externas ? leer(texto) : texto;
            if (!externas && /[^0-9]/.test(texto)) entrada = null;
        }
        const cambio = reemplazo(entrada, tipo);

        if (!evento.cancelable) {
            pendiente = cambio;
        } else if (moneda || !valido(cambio.cifras)) {
            evento.preventDefault();
            aplicar(cambio);
        }
    });

    for (const [tipo, origen] of [["paste", "clipboardData"], ["drop", "dataTransfer"]]) {
        campo.addEventListener(tipo, (evento) => {
            evento.preventDefault();
            pendiente = null;
            const texto = evento[origen]?.getData("text/plain");
            aplicar(reemplazo(texto ? leer(texto) : null, tipo));
        });
    }

    campo.addEventListener("input", (evento) => {
        if (pendiente) {
            const cambio = pendiente;
            pendiente = null;
            aplicar(cambio);
            return;
        }
        const eliminar = moneda && evento.inputType?.startsWith("delete")
            && /^[0-9$.]*$/.test(campo.value);
        const cifras = eliminar ? digitos(campo.value) : leer(campo.value);
        aplicar({
            cifras: eliminar && !Number(cifras) ? "" : cifras,
            restantes: digitos(campo.value.slice(campo.selectionStart)).length,
            seleccion: [campo.selectionStart, campo.selectionEnd],
        });
    });
}

function activarNombre(campo) {
    campo.addEventListener("input", () => {
        const nombre = campo.value.split(" ").filter(Boolean).join(" ");
        const minimo = Number(campo.dataset.nombreMin);
        const maximo = Number(campo.dataset.nombreMax);
        const longitud = Array.from(nombre).length;
        let mensaje = "";
        if (campo.value && (longitud < minimo || longitud > maximo)) {
            mensaje = `El nombre debe tener entre ${minimo} y ${maximo} caracteres.`;
        } else if (nombre && (!/\p{L}/u.test(nombre) || /[^\p{L} -]/u.test(nombre))) {
            mensaje = campo.dataset.errorNombre;
        }
        mostrarError(campo, mensaje);
    });
}

function activarContador(campo) {
    const contador = document.getElementById(`${campo.id}_contador`);
    const maximo = Number(campo.dataset.contador);
    campo.setAttribute("aria-describedby", contador.id);
    contador.hidden = false;
    function actualizar() {
        const longitud = campo.value.length;
        contador.textContent = `${longitud} / ${maximo} caracteres`;
        mostrarError(campo, longitud > maximo
            ? `La descripción no puede superar los ${maximo} caracteres.`
            : "");
    }
    actualizar();
    campo.addEventListener("input", actualizar);
}

document.querySelectorAll("[data-precio-clp]").forEach((campo) => activarNumero(campo, true));
document.querySelectorAll("[data-nombre-min]").forEach(activarNombre);
document.querySelectorAll("[data-contador]").forEach(activarContador);
document.querySelectorAll("[data-error-stock]").forEach((campo) => activarNumero(campo, false));
