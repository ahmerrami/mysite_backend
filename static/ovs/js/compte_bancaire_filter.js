(function($) {
    $(document).ready(function() {
        // Sélectionner les champs HTML correspondant au bénéficiaire et au compte bancaire
        const beneficiaireField = $('#id_beneficiaire');
        const compteBancaireField = $('#id_compte_bancaire');

        // Fonction pour mettre à jour les options du champ compte bancaire
        function updateCompteBancaireOptions() {
            // Récupérer la valeur (ID) du bénéficiaire sélectionné
            const beneficiaireId = beneficiaireField.val();

            if (beneficiaireId) { // Vérifier si un bénéficiaire est sélectionné
                // Effectuer une requête AJAX pour récupérer les comptes bancaires associés au bénéficiaire
                $.ajax({
                    url: '/api/ovs/get_comptes_bancaires/', // URL de l'API ou de la vue Django qui retourne les comptes bancaires
                    data: { 'beneficiaire_id': beneficiaireId }, // Envoyer l'ID du bénéficiaire en paramètre
                    dataType: 'json', // Spécifier que la réponse sera au format JSON
                    success: function(data) { // Fonction appelée en cas de succès
                        // Vider les options actuelles du champ compte bancaire
                        compteBancaireField.empty();
                        // Ajouter une option vide par défaut
                        compteBancaireField.append($("<option></option>").attr("value", "").text("---------"));
                        // Ajouter les nouvelles options basées sur les données reçues
                        $.each(data, function(key, value) {
                            compteBancaireField.append($("<option></option>").attr("value", key).text(value));
                        });
                    },
                    error: function(error) { // Fonction appelée en cas d'erreur
                        console.error("Erreur lors de la requête AJAX :", error);
                        // Optionnel : afficher un message d'erreur à l'utilisateur
                        alert("Une erreur est survenue lors du chargement des comptes bancaires.");
                    }
                });
            } else {
                // Si aucun bénéficiaire n'est sélectionné, réinitialiser le champ compte bancaire
                compteBancaireField.empty();
                compteBancaireField.append($("<option></option>").attr("value", "").text("---------")); // Option vide par défaut
            }
        }

        // Attacher un gestionnaire d'événements à l'événement "change" du champ bénéficiaire
        beneficiaireField.change(function() {
            // Mettre à jour les options de compte bancaire chaque fois que le bénéficiaire change
            updateCompteBancaireOptions();
        });

        // Appeler la fonction au chargement initial pour gérer le cas de la modification d'un formulaire existant
        updateCompteBancaireOptions();
    });
})(django.jQuery); // Utiliser l'objet jQuery de Django pour éviter les conflits avec d'autres versions de jQuery
