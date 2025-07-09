document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".sortie-row").forEach(row => {
        row.addEventListener("click", function () {
            let sortieId = this.getAttribute("data-sortie-id");
            let rameursRow = document.querySelector(".rameurs-row-" + sortieId);

            // Fermer toutes les autres lignes avant d'ouvrir celle-ci
            document.querySelectorAll("[class^='rameurs-row-']").forEach(row => {
                if (row !== rameursRow) {
                    row.style.display = "none";
                }
            });

            // Basculer l'affichage de la ligne sélectionnée
            if (rameursRow) {
                rameursRow.style.display = (rameursRow.style.display === "none" || rameursRow.style.display === "") ? "table-row" : "none";
            }
        });
    });

    // Gestion du filtrage des sorties
    document.getElementById("filtrerSorties").addEventListener("click", function () {
        let dateDebut = document.getElementById("dateDebut").value;
        let dateFin = document.getElementById("dateFin").value;

        // Modifier l'URL pour inclure les dates de filtrage
        let url = window.location.pathname + '?dateDebut=' + dateDebut + '&dateFin=' + dateFin;
        window.location.href = url;  // Rediriger vers l'URL mise à jour
    });
});
