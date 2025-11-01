// compte_tresorerie_filter.js
(function($) {
    $(document).ready(function() {
        const beneficiaireField = $('#id_beneficiaire');
        const compteTresorerieField = $('#id_compte_tresorerie');

        function updateCompteTresorerieOptions() {
            const beneficiaireId = beneficiaireField.val();
            const currentCompte = compteTresorerieField.val(); // Valeur actuelle du compte

            if (beneficiaireId) { // Vérifier si un bénéficiaire est sélectionné
                $.ajax({
                    url: '/api/fournisseurs/get_comptes_tresorerie/',
                    data: {
                        'beneficiaire_id': beneficiaireId
                    },
                    dataType: 'json',
                    success: function(data) {

                        if (!data || Object.keys(data).length === 0) {
                            console.error("Aucun compte tresorerie reçu.");
                            return;
                        }

                        const shouldPreserveCompte = currentCompte && currentCompte !== "";
                        compteTresorerieField.empty();
                        compteTresorerieField.append($("<option></option>").attr("value", "").text("------------"));

                        // Accéder directement à `data`, car `data.comptes` n'existe pas
                        $.each(data, function(key, value) {
                            compteTresorerieField.append($("<option></option>").attr("value", key).text(value));
                        });

                        // Vérifier et sélectionner le compte existant
                        if (data.compte_existant && data.hasOwnProperty(data.compte_existant)) {
                            compteTresorerieField.val(data.compte_existant);
                        } else if (shouldPreserveCompte && data.hasOwnProperty(currentCompte)) {
                            compteTresorerieField.val(currentCompte);
                        }
                    },
                    error: function(error) {
                        console.error("Erreur AJAX :", error);
                        alert("Erreur lors du chargement des comptes tresorerie.");
                    }
                });
            } else {
                compteTresorerieField.empty();
                compteTresorerieField.append($("<option></option>").attr("value", "").text("---------"));
            }
        }

        beneficiaireField.change(updateCompteTresorerieOptions);
        updateCompteTresorerieOptions(); // Appel initial
    });
})(django.jQuery);