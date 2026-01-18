document.addEventListener('DOMContentLoaded', function () {

    const offcanvas = document.getElementById('offcanvasFiltro');

    if (!offcanvas) return; // não existe filtro nessa página

    offcanvas.addEventListener('show.bs.offcanvas', function () {

        // Limpa inputs
        offcanvas.querySelectorAll('input').forEach(input => {
            if (input.type !== 'hidden') {
                input.value = '';
            }
        });

        // Reseta selects
        offcanvas.querySelectorAll('select').forEach(select => {
            select.selectedIndex = 0;
        });
    });
});
