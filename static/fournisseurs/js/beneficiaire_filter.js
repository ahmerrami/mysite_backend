// beneficiaire_filter.js
(function($) {
    $(document).ready(function() {
        var type_ov_field = $('#id_type_ov'); // ID du champ type_ov
        var beneficiaire_field = $('#id_beneficiaire'); // ID du champ beneficiaire
        var compteBancaireField = $('#id_compte_bancaire');

        function update_beneficiaires() {
            var selected_type = type_ov_field.val();
            var current_value = beneficiaire_field.val(); // Récupère la valeur actuelle du champ beneficiaire

            $.ajax({
                url: '/api/fournisseurs/get_beneficiaires/', // URL de la vue Django
                data: { 'type_ov': selected_type },
                dataType: 'json',
                success: function(data) {
                    var should_preserve_value = current_value && current_value !== ""; // Vérifie si une valeur est déjà définie

                    beneficiaire_field.empty(); // Vide les options actuelles
                    beneficiaire_field.append($("<option></option>").attr("value", "").text("---------")); // Ajoute une option vide
                    compteBancaireField.empty(); // Vide les options actuelles
                    compteBancaireField.append($("<option></option>").attr("value", "").text("---------")); // Ajoute une option vide

                    $.each(data, function(key, value) {
                        beneficiaire_field.append($("<option></option>").attr("value", key).text(value));
                    });

                    // Si une valeur existante doit être préservée, la sélectionner à nouveau
                    if (should_preserve_value && data[current_value]) {
                        beneficiaire_field.val(current_value);
                    }
                }
            });
        }

        type_ov_field.change(function() {
            update_beneficiaires();
        });

        // Appeler la fonction au chargement initial de la page pour gérer le cas où un type est déjà sélectionné lors de la modification
        update_beneficiaires();
    });
})(django.jQuery);
