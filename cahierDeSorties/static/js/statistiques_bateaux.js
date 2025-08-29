document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const table = document.getElementById("bateauxTable");
    const rows = table && table.tBodies.length > 0 ? table.tBodies[0].rows : [];

    // Accordéon : un seul détail ouvert à la fois, toggle sur la même ligne
    document.querySelectorAll('.bateau-row').forEach(function(row) {
        row.addEventListener('click', function(e) {
            // Ignore le clic sur un bouton dans la ligne
            if (e.target.closest('button')) return;

            const detailId = row.getAttribute('data-detail');
            const detailRow = document.getElementById(detailId);
            if (!detailRow) return;

            const isOpen = window.getComputedStyle(detailRow).display !== 'none';

            // Ferme tous les détails
            document.querySelectorAll('.bateau-detail-row').forEach(function(d) {
                d.style.display = 'none';
            });

            // Toggle : si déjà ouvert, on ferme, sinon on ouvre
            if (!isOpen) {
                detailRow.style.display = 'table-row';
            }
        });
    });

    // Gestion du bouton armer en couple/pointe
    document.querySelectorAll('.btn-armer-mode').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const bateauId = btn.dataset.bateauId;
            const mode = btn.dataset.mode;
            const modeLabel = mode === "couple" ? "couple" : "pointe";
            if (confirm(`Voulez-vous vraiment armer ce bateau en ${modeLabel} ?`)) {
                fetch(`/bateaux/armer_mode/${bateauId}/${mode}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert("Erreur : " + (data.error || "action impossible"));
                    }
                });
            }
        });
    });

    // Recherche
    if (searchInput && table) {
        searchInput.addEventListener("input", function() {
            const filter = searchInput.value.toLowerCase();
            for (let i = 0; i < rows.length; i += 2) {
                const row = rows[i];
                const detailRow = rows[i + 1];
                if (row && row.classList.contains('bateau-row')) {
                    const text = row.textContent.toLowerCase();
                    const show = text.indexOf(filter) > -1;
                    row.style.display = show ? "" : "none";
                    if (detailRow) detailRow.style.display = "none";
                }
            }
        });
    }

    // Fonction utilitaire pour CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});