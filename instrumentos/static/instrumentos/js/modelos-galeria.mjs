import {geometriaGuitarra} from "./guitarra-geometria.mjs";
import {crearMalla} from "./malla-instrumentos.mjs";

function geometriaTeclado() {
    const {caja, vertices} = crearMalla();
    const negro = [.06, .055, .065], blanco = [.92, .88, .79], metal = [.38, .4, .42];
    caja([0, -.10, 0], [3.1, .27, 1.13], negro, true);
    caja([0, .047, -.30], [2.94, .025, .47], negro);
    caja([0, .065, -.33], [.49, .03, .185], metal);
    caja([0, .085, -.33], [.43, .016, .14], [.16, .49, .63]);
    for (let i = 0; i < 21; i++) {
        const x = (i - 10) * .132;
        caja([x, .056, .225], [.127, .035, .61], blanco);
        if (i < 20 && [0, 1, 3, 4, 5].includes(i % 7)) {
            caja([x + .066, .09, .125], [.074, .05, .39], negro);
        }
    }
    for (const lado of [-1, 1]) {
        for (let i = 0; i < 6; i++) {
            const x = lado * (.38 + i * .143);
            caja([x, .065, -.24], [.10, .028, .075], i === 0 ? [.67, .16, .09] : metal);
            caja([x, .073, -.42], [.073, .055, .074], negro);
        }
    }
    return vertices();
}

function geometriaBateria() {
    const {cilindro, vertices} = crearMalla();
    const metal = [.59, .61, .64], parche = [.83, .75, .61];
    const negro = [.105, .09, .085], bronce = [.76, .46, .13];
    function tambor([x, y, z], radio, altura, bombo = false) {
        const a = bombo ? [x, y, z - altura / 2] : [x, y - altura / 2, z];
        const b = bombo ? [x, y, z + altura / 2] : [x, y + altura / 2, z];
        const eje = bombo ? [0, 0, 1] : [0, 1, 0];
        cilindro(a, b, radio, radio, negro, true);
        for (const [extremo, sentido] of [[a, -1], [b, 1]]) {
            const borde = extremo.map((valor, i) => valor + eje[i] * sentido * .035);
            const tapa = borde.map((valor, i) => valor + eje[i] * sentido * .007);
            cilindro(extremo, borde, radio + .025, radio + .025, metal);
            cilindro(borde, tapa, radio - .02, radio - .02, bombo ? negro : parche);
        }
    }
    function soporte(x, y, z) {
        cilindro([x, -.94, z], [x, y, z], .025, .018, metal);
        for (let i = 0; i < 3; i++) {
            const angulo = i * 2 * Math.PI / 3;
            cilindro([x, -.70, z], [x + .30 * Math.cos(angulo), -.98, z + .30 * Math.sin(angulo)], .018, .016, metal);
        }
    }
    tambor([0, -.32, .36], .56, .64, true);
    tambor([-.34, .37, .17], .29, .34);
    tambor([.31, .40, .09], .31, .36);
    tambor([.84, -.21, -.18], .37, .50);
    tambor([-.86, .02, .25], .32, .20);
    soporte(.84, -.35, -.18);
    soporte(-.86, -.05, .25);
    for (const [x, y, z, radio] of [[-1.09, .90, -.25, .43], [.99, .99, -.37, .49], [-1.22, .39, .49, .29]]) {
        soporte(x, y + .08, z);
        cilindro([x, y - .034, z], [x, y, z], radio, radio, bronce);
        cilindro([x, y, z], [x, y + .057, z], radio, radio * .25, bronce);
        cilindro([x, y + .056, z], [x, y + .085, z], .039, .028, metal);
    }
    return vertices();
}

export const modelos = {
    guitarras: {malla: geometriaGuitarra, orientacion: [-.34, -.12], escala: .51, anchoMinimo: .72},
    bajos: {malla: () => geometriaGuitarra(true), orientacion: [-.34, -.12], escala: .42, anchoMinimo: .72},
    teclados: {malla: geometriaTeclado, orientacion: [-.28, .63], escala: .52, anchoMinimo: 1.23},
    baterias: {malla: geometriaBateria, orientacion: [-.22, .21], escala: .52, anchoMinimo: 1.30},
};
