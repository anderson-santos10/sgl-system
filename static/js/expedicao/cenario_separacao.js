document.addEventListener("DOMContentLoaded", function () {

    const cards = document.querySelectorAll(".separacao-card");

    cards.forEach(card => {
        card.addEventListener("click", function () {
            const url = this.dataset.url;
            if (url) {
                window.location.href = url;
            }
        });

        card.style.cursor = "pointer";
    });

});
