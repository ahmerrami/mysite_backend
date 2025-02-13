//dynamic_factures.js
document.addEventListener('DOMContentLoaded', function () {
    const beneficiaireField = document.getElementById('id_beneficiaire'); // Champ bénéficiaire
    const ordreVirementId = document.getElementById('id_ordre_virement_id').value;
    const facturesContainer = document.getElementById('id_factures'); // Conteneur des factures

    // Fonction pour charger les factures
    function loadFactures(beneficiaireId) {
        if (!beneficiaireId) {
            facturesContainer.innerHTML = '<p>Aucun bénéficiaire sélectionné.</p>';
            return;
        }

        // Construction de l'URL
        let url = `/api/fournisseurs/get-factures/?beneficiaire_id=${beneficiaireId}`;
        if (ordreVirementId) {
            url += `&ordre_virement_id=${ordreVirementId}`;
        }

        // Requête vers l'API
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    let html = '';
                    data.forEach(facture => {
                        const isChecked = facture.ordre_virement !== null;

                        // Construction du HTML pour chaque facture
                        html += `
                            <li>
                                <label>
                                    <input type="checkbox" name="factures" value="${facture.id}" ${isChecked ? 'checked' : ''}>
                                    ${facture.num_facture} - Montant : ${facture.montant_ttc} - Mnt net à payer : ${facture.mnt_net_apayer} - Échéance : ${facture.date_echeance}
                                </label>
                            </li>
                        `;
                    });
                    facturesContainer.innerHTML = html; // Injection du HTML dans le conteneur
                } else {
                    facturesContainer.innerHTML = '<p>Aucune facture trouvée...</p>';
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

        // Chargement initial si un bénéficiaire est déjà sélectionné
        if (beneficiaireField.value) {
            loadFactures(beneficiaireField.value);
        }
    }
});