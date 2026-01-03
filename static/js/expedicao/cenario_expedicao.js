// static/js/expedicao/clickable_rows.js
document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll(".clickable-row");

    rows.forEach(row => {
        // Cursor de clique
        row.style.cursor = "pointer";

        // Hover visual
        row.addEventListener("mouseenter", () => {
            row.style.backgroundColor = "#f1f8ff"; // cor leve de destaque
        });
        row.addEventListener("mouseleave", () => {
            row.style.backgroundColor = ""; // volta ao normal
        });

        // Clique redireciona para edição
        row.addEventListener("click", () => {
            if (row.dataset.href) {
                window.location.href = row.dataset.href;
            }
        });
    });
});
