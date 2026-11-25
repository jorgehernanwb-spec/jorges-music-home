const assert = require("node:assert/strict");
const {readFile} = require("node:fs/promises");
const test = require("node:test");

test("los cuatro GLB cargan con el mismo GLTFLoader y conservan piezas y texturas", async () => {
    const {GLTFLoader} = await import("../static/instrumentos/vendor/three-0.180.0/GLTFLoader.mjs");
    const {Box3, Vector3} = await import("../static/instrumentos/vendor/three-0.180.0/three.module.min.mjs");
    const {modelos, urlModelo, esPiezaPintable} = await import("../static/instrumentos/js/modelos-glb.mjs");
    const {encuadrar, prepararAcabado} = await import("../static/instrumentos/js/galeria-glb.mjs");
    globalThis.self = globalThis;
    // Node verifica las PNG incrustadas y su conexión al material. El navegador decodifica los píxeles.
    globalThis.createImageBitmap = async (blob) => {
        const datos = new DataView(await blob.arrayBuffer());
        assert.equal(datos.getUint32(0), 0x89504e47);
        return {width: datos.getUint32(16), height: datos.getUint32(20)};
    };
    try {
        const esperados = {
            guitarras: ["solid-body-electric-guitar.glb", 107, 1, 1],
            bajos: ["four-string-bass-guitar.glb", 89, 1, 1],
            teclados: ["88-key-keyboard-instrument.glb", 128, 3, 0],
            baterias: ["five-piece-drum-kit.glb", 322, 4, 0],
        };
        assert.deepEqual(Object.keys(modelos), Object.keys(esperados));
        for (const [sala, modelo] of Object.entries(modelos)) {
            const [archivo, cantidad, pintables, ejePrincipal] = esperados[sala];
            assert.equal(modelo.archivo, archivo);
            const datos = await readFile(urlModelo(modelo));
            assert.equal(datos.toString("ascii", 0, 4), "glTF");
            assert.equal(datos.readUInt32LE(4), 2);
            assert.equal(datos.readUInt32LE(8), datos.length);
            const {scene} = await new GLTFLoader().parseAsync(Uint8Array.from(datos).buffer, "");
            const mallas = [];
            scene.traverse((objeto) => { if (objeto.isMesh) mallas.push(objeto); });
            assert.equal(mallas.length, cantidad);
            const piezas = mallas.filter((objeto) => esPiezaPintable(objeto, modelo));
            assert.equal(piezas.length, pintables);
            const naturales = mallas.filter((objeto) => !piezas.includes(objeto));
            const materiales = naturales.map((objeto) => objeto.material);
            const texturas = piezas.map((objeto) => objeto.material.map);
            const acabado = prepararAcabado(scene, modelo);
            for (const color of ["#CF3434", "#2975CD", "#232323", "#F1F0E9", "#8650C0"]) {
                acabado.aplicar(color);
                for (const [indice, pieza] of piezas.entries()) {
                    assert.equal(pieza.material.color.getHexString(), color.slice(1).toLowerCase());
                    assert.equal(pieza.material.map, texturas[indice]);
                    assert.ok(pieza.material.map.image.width > 0);
                }
            }
            assert.deepEqual(naturales.map((objeto) => objeto.material), materiales);
            const antes = new Box3().setFromObject(scene, true).getSize(new Vector3());
            assert.equal(antes.toArray()[ejePrincipal], Math.max(...antes.toArray()));
            const normalizado = new Box3().setFromObject(encuadrar(scene), true);
            assert.ok(normalizado.getCenter(new Vector3()).length() < 1e-6);
            assert.ok(Math.abs(normalizado.getSize(new Vector3()).length() - 2) < 1e-6);
        }
    } finally {
        delete globalThis.self;
        delete globalThis.createImageBitmap;
    }
});

test("sin WebGL 2 se mantienen el aviso y las especificaciones del carrusel", async () => {
    const {iniciarVisor} = await import("../static/instrumentos/js/galeria-visor.mjs");
    const aviso = {hidden: false};
    const canvas = {hidden: true, getContext: () => null};
    const controles = {hidden: true, contains: () => false};
    const elementos = new Map([
        ["[data-visor]", canvas], ["[data-visor-alternativo]", aviso],
        ["[data-visor-controles]", controles],
    ]);
    const pagina = {querySelector: (selector) => elementos.get(selector) ?? null};
    const entorno = {matchMedia: () => ({matches: true}), cancelAnimationFrame: () => {}};
    assert.equal(iniciarVisor(pagina, entorno), false);
    assert.match(aviso.textContent, /Visor 3D no disponible/);
    assert.equal(aviso.hidden, false);
    assert.equal(canvas.hidden, true);
    assert.equal(controles.hidden, true);
});
