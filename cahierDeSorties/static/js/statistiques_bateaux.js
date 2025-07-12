document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const table = document.getElementById("bateauxTable");
    const rows = table.tBodies[0].rows;

    searchInput.addEventListener("input", function() {
        const filter = searchInput.value.toLowerCase();

        for (let row of rows) {
            const bateauNom = row.cells[0].textContent.toLowerCase();

            if (bateauNom.includes(filter)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }
    });
});
