document.addEventListener('DOMContentLoaded', function () {
    const beneficiaireField = document.getElementById('id_beneficiaire'); // Champ bénéficiaire
    const facturesContainer = document.getElementById('id_factures'); // Conteneur des factures

    // Fonction pour charger les factures non affectées
    function loadFactures(beneficiaireId) {
        if (!beneficiaireId) {
            facturesContainer.innerHTML = '<p>Aucun bénéficiaire sélectionné.</p>';
            return;
        }

        // Effectue une requête AJAX vers la vue Django
        fetch(`/api/ovs/get-factures/?beneficiaire_id=${beneficiaireId}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    let html = '';
                    data.forEach(facture => {
                        html += `
                            <label>
                                <input type="checkbox" name="factures" value="${facture.id}">
                                ${facture.num_facture} - Montant : ${facture.montant_ttc} - Échéance : ${facture.date_echeance}
                            </label><br>
                        `;
                    });
                    facturesContainer.innerHTML = html;
                } else {
                    facturesContainer.innerHTML = '<p>Aucune facture non affectée.</p>';
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des factures :', error);
                facturesContainer.innerHTML = '<p>Erreur de chargement.</p>';
            });
    }

    // Écouteur pour le changement du champ bénéficiaire
    if (beneficiaireField) {
        beneficiaireField.addEventListener('change', function () {
            const beneficiaireId = this.value;
            loadFactures(beneficiaireId);
        });
    }
});
