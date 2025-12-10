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
                    // Construction du tableau HTML
                    let html = `
                        <table class="factures-table" style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                            <thead>
                                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                    <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6; width: 60px;">Sélection</th>
                                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">N° Facture</th>
                                    <th style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">Montant TTC</th>
                                    <th style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">Net à payer</th>
                                    <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Échéance</th>
                                    <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Statut</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    data.forEach(facture => {
                        const isChecked = facture.ordre_virement !== null;
                        
                        // Définir la couleur du statut
                        let statutColor = '#6c757d'; // Gris par défaut
                        let statutBg = '#f8f9fa';
                        if (facture.statut === 'en_attente_signature') {
                            statutColor = '#856404';
                            statutBg = '#fff3cd';
                        } else if (facture.statut === 'signee') {
                            statutColor = '#004085';
                            statutBg = '#cce5ff';
                        } else if (facture.statut === 'remise_a_banque') {
                            statutColor = '#0c5460';
                            statutBg = '#d1ecf1';
                        } else if (facture.statut === 'reglee') {
                            statutColor = '#155724';
                            statutBg = '#d4edda';
                        }
                        
                        html += `
                            <tr style="border-bottom: 1px solid #dee2e6; ${isChecked ? 'background-color: #e7f3ff;' : ''}">
                                <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6;">
                                    <input type="checkbox" name="factures" value="${facture.id}" ${isChecked ? 'checked' : ''}>
                                </td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">
                                    <strong>${facture.num_facture}</strong>
                                </td>
                                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6;">
                                    ${parseFloat(facture.montant_ttc).toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} DH
                                </td>
                                <td style="padding: 8px; text-align: right; border: 1px solid #dee2e6; font-weight: bold;">
                                    ${parseFloat(facture.mnt_net_apayer).toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} DH
                                </td>
                                <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6;">
                                    ${facture.date_echeance}
                                </td>
                                <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6;">
                                    <span style="padding: 4px 8px; border-radius: 4px; background-color: ${statutBg}; color: ${statutColor}; font-size: 12px; font-weight: 500;">
                                        ${facture.statut_display || facture.statut}
                                    </span>
                                </td>
                            </tr>
                        `;
                    });
                    
                    html += `
                            </tbody>
                        </table>
                    `;
                    
                    facturesContainer.innerHTML = html;

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