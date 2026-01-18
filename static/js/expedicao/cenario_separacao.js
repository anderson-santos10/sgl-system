document.addEventListener("DOMContentLoaded", function () {
    const subcards = document.querySelectorAll(".sgl-subcard");

    subcards.forEach(card => {
        card.style.cursor = "pointer";
        card.addEventListener("click", function (e) {
            e.stopPropagation(); // evita clique no card principal
            const url = this.dataset.url;
            if (url) {
                window.location.href = url;
            }
        });
    });
});
