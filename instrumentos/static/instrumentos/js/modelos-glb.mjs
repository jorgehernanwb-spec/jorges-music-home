const cuerpo = "Original_carved_solid_instrument_body";

export const modelos = {
    guitarras: {archivo: "solid-body-electric-guitar.glb", orientacion: [-.30, -.10],
        margen: 1.12, piezas: [cuerpo], material: "red"},
    bajos: {archivo: "four-string-bass-guitar.glb", orientacion: [-.30, -.10],
        margen: 1.12, piezas: [cuerpo], material: "blue"},
    teclados: {archivo: "88-key-keyboard-instrument.glb", orientacion: [-.22, .54], margen: 1.10,
        piezas: ["Keyboard_lower_housing", "Keyboard_end_cheek", "Keyboard_end_cheek001"], material: "black"},
    baterias: {archivo: "five-piece-drum-kit.glb", orientacion: [-.23, .22], margen: 1.06,
        piezas: [
            "10_inch_mounted_tom_finite_wood_shell", "12_inch_mounted_tom_finite_wood_shell",
            "16_inch_floor_tom_finite_wood_shell", "22_inch_bass_drum_finite_wood_shell",
        ], material: "blue"},
};

export function urlModelo(modelo) {
    return new URL(`../modelos/${modelo.archivo}`, import.meta.url);
}

export function esPiezaPintable(objeto, modelo) {
    return objeto.isMesh && objeto.material?.name === modelo.material && modelo.piezas.includes(objeto.name);
}
