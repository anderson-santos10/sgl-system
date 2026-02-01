document.addEventListener('DOMContentLoaded', function () {

    /* ========= FILTRO OFFCANVAS ========= */
    const offcanvas = document.getElementById('offcanvasFiltro');

    if (offcanvas) {
        offcanvas.addEventListener('show.bs.offcanvas', function () {

            offcanvas.querySelectorAll('input').forEach(input => {
                if (input.type !== 'hidden') {
                    input.value = '';
                }
            });

            offcanvas.querySelectorAll('select').forEach(select => {
                select.selectedIndex = 0;
            });
        });
    }

    /* ========= LINHA CLICÁVEL ========= */
    document.querySelectorAll("tr.row-clickable").forEach(function (row) {

        row.addEventListener("click", function (e) {

            // se clicar em link ou botão, não redireciona
            if (e.target.closest("a") || e.target.closest("button")) return;

            const url = this.dataset.url;
            if (url) {
                window.location.href = url;
            }
        });

        row.style.cursor = "pointer";
    });

});
