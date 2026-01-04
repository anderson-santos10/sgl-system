document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('tr[data-href]');
    rows.forEach(row => {
        row.style.cursor = 'pointer'; // deixa o cursor como link
        row.addEventListener('click', () => {
            window.location.href = row.dataset.href;
        });
    });
});
