(function($) {
    $(document).ready(function() {
        const beneficiaireField = $('#id_beneficiaire');
        const compteBancaireField = $('#id_compte_bancaire');

        function updateCompteBancaireOptions() {
            const beneficiaireId = beneficiaireField.val();
            const currentCompte = compteBancaireField.val(); // Valeur actuelle du compte

            if (beneficiaireId) { // Vérifier si un bénéficiaire est sélectionné
                $.ajax({
                    url: '/api/ovs/get_comptes_bancaires/',
                    data: {
                        'beneficiaire_id': beneficiaireId
                    },
                    dataType: 'json',
                    success: function(data) {

                        if (!data || Object.keys(data).length === 0) {
                            console.error("Aucun compte bancaire reçu.");
                            return;
                        }

                        const shouldPreserveCompte = currentCompte && currentCompte !== "";
                        compteBancaireField.empty();
                        compteBancaireField.append($("<option></option>").attr("value", "").text("------------"));

                        // Accéder directement à `data`, car `data.comptes` n'existe pas
                        $.each(data, function(key, value) {
                            compteBancaireField.append($("<option></option>").attr("value", key).text(value));
                        });

                        // Vérifier et sélectionner le compte existant
                        if (data.compte_existant && data.hasOwnProperty(data.compte_existant)) {
                            compteBancaireField.val(data.compte_existant);
                        } else if (shouldPreserveCompte && data.hasOwnProperty(currentCompte)) {
                            compteBancaireField.val(currentCompte);
                        }
                    },
                    error: function(error) {
                        console.error("Erreur AJAX :", error);
                        alert("Erreur lors du chargement des comptes bancaires.");
                    }
                });
            } else {
                compteBancaireField.empty();
                compteBancaireField.append($("<option></option>").attr("value", "").text("---------"));
            }
        }

        beneficiaireField.change(updateCompteBancaireOptions);
        updateCompteBancaireOptions(); // Appel initial
    });
})(django.jQuery);