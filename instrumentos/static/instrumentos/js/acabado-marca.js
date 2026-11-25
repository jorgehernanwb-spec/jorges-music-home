const marca = document.getElementById("id_marca");
const acabado = document.getElementById("acabado-marca");
const muestra = acabado.querySelector("span");
const coloresMarca = new Map(Object.entries(JSON.parse(document.getElementById("colores-marca").textContent)));

marca.addEventListener("change", () => {
    const color = coloresMarca.get(marca.value);
    acabado.hidden = !color;
    if (color) muestra.style.setProperty("--acabado", color);
    else muestra.style.removeProperty("--acabado");
});
