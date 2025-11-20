document.querySelectorAll('.leaderboard-row').forEach(row => {
    row.addEventListener('click', () => {
        const rameurId = row.dataset.rameurId;
        window.location.href = `/rameurs/statistiques-rameurs/?rameur_id=${rameurId}`;
    });
});