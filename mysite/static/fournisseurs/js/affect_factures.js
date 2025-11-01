// affect_factures.js
document.addEventListener('DOMContentLoaded', function () {
    const beneficiaireField = document.getElementById('id_beneficiaire'); // Champ bénéficiaire
    const ordreVirementId = document.getElementById('id_ordre_virement_id').value; // ID de l'ordre de virement
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

        // Requête vers l'API pour charger les factures
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

                    // Ajouter les écouteurs d'événements pour les cases à cocher
                    addCheckboxEventListeners();
                } else {
                    facturesContainer.innerHTML = '<p>Aucune facture trouvée...</p>';
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des factures :', error);
                facturesContainer.innerHTML = '<p>Erreur de chargement.</p>';
            });
    }

    // Fonction pour ajouter des écouteurs d'événements aux cases à cocher
    function addCheckboxEventListeners() {
        const checkboxes = facturesContainer.querySelectorAll('input[type="checkbox"][name="factures"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                const factureId = this.value;
                const isChecked = this.checked;

                // Mettre à jour l'association de la facture
                updateFactureAssociation(factureId, isChecked);
            });
        });
    }

    // Fonction pour mettre à jour l'association d'une facture
    function updateFactureAssociation(factureId, isChecked) {
        const url = '/api/fournisseurs/update-facture-association/';
        const data = {
            facture_id: Number(factureId),  // ✅ Conversion en entier
            ordre_virement_id: Number(ordreVirementId),  // ✅ Conversion en entier
            is_associated: Boolean(isChecked)
        };

        console.log("Données envoyées :", data); // Debugging

        // Envoyer une requête POST pour mettre à jour l'association
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Si vous utilisez CSRF protection
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Association mise à jour avec succès');
            } else {
                console.error('Erreur lors de la mise à jour de l\'association :', data.error);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour de l\'association :', error);
        });
    }

    // Fonction pour récupérer le cookie CSRF (si nécessaire)
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