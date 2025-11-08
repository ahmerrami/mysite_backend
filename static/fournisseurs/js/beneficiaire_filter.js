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
                url: '/api/fournisseurs/get_beneficiaires/',
                data: { 
                    'type_ov': selected_type,
                    'filtre_factures_attente': 'true'  // Filtrer par factures en attente
                },
                dataType: 'json',
                success: function(data) {
                    var should_preserve_value = current_value && current_value !== "";

                    beneficiaire_field.empty();
                    beneficiaire_field.append($("<option></option>").attr("value", "").text("---------"));
                    compteBancaireField.empty();
                    compteBancaireField.append($("<option></option>").attr("value", "").text("---------"));

                    // Convertir les données en tableau et les trier
                    var sortedData = Object.keys(data).map(function(key) {
                        return { key: key, value: data[key] };
                    }).sort(function(a, b) {
                        return a.value.toLowerCase().localeCompare(b.value.toLowerCase());
                    });

                    // Ajouter les options triées
                    sortedData.forEach(function(item) {
                        beneficiaire_field.append($("<option></option>").attr("value", item.key).text(item.value));
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
