document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const btnSalvar = document.getElementById("btnSalvar");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    form.addEventListener("submit", function () {
        btnText.innerText = "Salvando...";
        btnLoader.classList.remove("d-none");
        btnSalvar.disabled = true;
    });
});


function renderCargas() {
    const qtd = parseInt(seqInput.value) || 0;
    cargasContainer.innerHTML = "";

    for (let i = 0; i < qtd; i++) {
        const cargaExistente = window.cargasExistentes[i] || {};
        cargasContainer.innerHTML += `
            <div class="col-md-4">
                <div class="border rounded-3 p-3 h-100 bg-light">
                    <strong class="text-primary small d-block mb-2">
                        Carga ${i + 1}
                    </strong>

                    <input type="text" name="carga[]" class="form-control form-control-sm mb-2"
                           placeholder="Carga" value="${cargaExistente.carga || ''}" required>

                    <input type="number" name="seq[]" class="form-control form-control-sm mb-2"
                           placeholder="Seq" value="${cargaExistente.seq || i + 1}">

                    <input type="number" name="total_entregas[]" class="form-control form-control-sm mb-2"
                           placeholder="Entregas" value="${cargaExistente.total_entregas || ''}">

                    <input type="text" name="mod[]" class="form-control form-control-sm"
                           placeholder="MOD" value="${cargaExistente.mod || ''}">
                </div>
            </div>
        `;
    }
}
