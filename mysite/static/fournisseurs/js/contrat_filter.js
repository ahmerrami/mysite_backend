// contrat_filter.js
(function($) {
    $(document).ready(function() {
        const beneficiaireField = $('#id_beneficiaire');
        const contratField = $('#id_contrat');

        function updateContratOptions() {
            const beneficiaireId = beneficiaireField.val();
            const currentContrat = contratField.val(); // Valeur actuelle du contrat

            if (beneficiaireId) { // Vérifier si un bénéficiaire est sélectionné
                $.ajax({
                    url: '/api/fournisseurs/get-contrats/', // Modifier l'URL pour les contrats
                    data: {
                        'beneficiaire_id': beneficiaireId
                    },
                    dataType: 'json',
                    success: function(data) {

                        if (!data || Object.keys(data).length === 0) {
                            console.error("Aucun contrat reçu.");
                            return;
                        }

                        const shouldPreserveContrat = currentContrat && currentContrat !== "";
                        contratField.empty();
                        contratField.append($("<option></option>").attr("value", "").text("------------"));

                        // Accéder directement à `data`, car `data.contrats` n'existe pas
                        $.each(data, function(key, value) {
                            contratField.append($("<option></option>").attr("value", key).text(value));
                        });

                        // Vérifier et sélectionner le contrat existant
                        if (data.contrat_existant && data.hasOwnProperty(data.contrat_existant)) {
                            contratField.val(data.contrat_existant);
                        } else if (shouldPreserveContrat && data.hasOwnProperty(currentContrat)) {
                            contratField.val(currentContrat);
                        }
                    },
                    error: function(error) {
                        console.error("Erreur AJAX :", error);
                        alert("Erreur lors du chargement des contrats.");
                    }
                });
            } else {
                contratField.empty();
                contratField.append($("<option></option>").attr("value", "").text("---------"));
            }
        }

        beneficiaireField.change(updateContratOptions);
        updateContratOptions(); // Appel initial
    });
})(django.jQuery);