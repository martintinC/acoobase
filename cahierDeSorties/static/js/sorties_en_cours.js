document.addEventListener("DOMContentLoaded", function() {
    let bateauSelect = document.getElementById("selectBateau");
    let rameursContainer = document.getElementById("rameursContainer");

    bateauSelect.addEventListener("change", function() {
        let bateauId = this.value;
        rameursContainer.innerHTML = "";  // Effacer les anciens champs

        if (bateauId) {
            let url = getRameursUrlBase.replace("0", bateauId); // Remplace '0' par l'ID du bateau sélectionné
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log("Réponse AJAX :", data);  // DEBUG : Voir la réponse dans la console

                    if (data.nombre_rameurs) {
                        let rowDiv = document.createElement("div");
                        rowDiv.classList.add("row");

                        for (let i = 0; i < data.nombre_rameurs; i++) {
                            let colDiv = document.createElement("div");
                            colDiv.classList.add("col-md-6", "mb-2");

                            let select = document.createElement("select");
                            select.name = "rameurs[]";
                            select.classList.add("form-control");

                            let optionPlaceholder = document.createElement("option");
                            optionPlaceholder.textContent = "-- Choisir un rameur --";
                            optionPlaceholder.value = "";
                            select.appendChild(optionPlaceholder);

                            data.rameurs.forEach(rameur => {
                                let option = document.createElement("option");
                                option.value = rameur.id;
                                option.textContent = rameur.prenom + " " + rameur.nom;
                                select.appendChild(option);
                            });

                            colDiv.appendChild(select);
                            rowDiv.appendChild(colDiv);
                        }

                        rameursContainer.appendChild(rowDiv);
                    }
                })
                .catch(error => console.error("Erreur AJAX :", error));
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    let form = document.getElementById("ajoutSortieForm");
    if (form) {  // Vérifie que le formulaire existe avant d'ajouter l'eventListener
        form.addEventListener("submit", function(event) {
            event.preventDefault();
            let formData = new FormData(this);

            fetch(ajouterSortieUrl, {  // Utilise la variable définie dans le HTML
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert("Erreur lors de l'ajout de la sortie !");
                }
            })
            .catch(error => console.error("Erreur :", error));
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    let sortieOuverte = null; // Stocke l'ID de la sortie ouverte

    document.querySelectorAll(".sortie-row").forEach(function(row) {
        row.addEventListener("click", function() {
            const sortieId = this.getAttribute("data-sortie-id");
            const rameursRow = document.querySelector(".rameurs-row-" + sortieId);

            if (sortieOuverte && sortieOuverte !== sortieId) {
                // Fermer l'ancienne sortie ouverte
                document.querySelector(".rameurs-row-" + sortieOuverte).style.display = "none";
            }

            // Si on clique sur la même sortie, on la ferme
            if (rameursRow.style.display === "table-row") {
                rameursRow.style.display = "none";
                sortieOuverte = null; // Réinitialise l'ID de la sortie ouverte
            } else {
                rameursRow.style.display = "table-row";
                sortieOuverte = sortieId; // Stocke la nouvelle sortie ouverte
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".supprimer-sortie").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation();  // Empêcher la propagation du clic au `tr`
            let sortieId = this.getAttribute("data-sortie-id");

            let supprimerSortieUrl = supprimerSortieUrlBase.replace('0', sortieId);  // Remplacer '0' par l'ID de la sortie

            if (confirm("Voulez-vous vraiment supprimer cette sortie ?")) {
                fetch(supprimerSortieUrl, {  // Utilisation de l'URL correcte
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();  // Recharger la page
                    } else {
                        alert("Erreur lors de la suppression !");
                    }
                })
                .catch(error => console.error("Erreur :", error));
            }
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".valider-sortie").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation();  // Empêcher la propagation du clic au `tr`
            let sortieId = this.getAttribute("data-sortie-id");
            let kilometres = document.getElementById("distance_" + sortieId).value;

            if (!kilometres || kilometres <= 0) {
                alert("Veuillez entrer un nombre de kilomètres valide.");
                return;
            }

            let finSortie = new Date();  // Heure actuelle pour la fin de la sortie
            let heures = finSortie.getHours().toString().padStart(2, "0");
            let minutes = finSortie.getMinutes().toString().padStart(2, "0");
            let finSortieFormatted = `${heures}:${minutes}`;  // Format "HH:mm"

            // Envoi des données au serveur pour enregistrer la sortie avec le nombre de km et l'heure de fin
            fetch(`/sorties/valider-sortie/${sortieId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    kilometres: kilometres,
                    fin: finSortieFormatted
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();  // Recharger la page pour mettre à jour la sortie
                } else {
                    alert("Erreur lors de l'enregistrement des données !");
                }
            })
            .catch(error => console.error("Erreur :", error));
        });
    });
});





