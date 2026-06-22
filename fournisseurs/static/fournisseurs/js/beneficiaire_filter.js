// beneficiaire_filter.js
(function($) {
    $(document).ready(function() {
        var type_ov_field = $('#id_type_ov'); // ID du champ type_ov
        var beneficiaire_field = $('#id_beneficiaire'); // ID du champ beneficiaire
        var compteBancaireField = $('#id_compte_bancaire');
        var is_change_form = $('body').hasClass('change-form');

        function update_beneficiaires() {
            var selected_type = type_ov_field.val();
            var current_value = beneficiaire_field.val(); // Récupère la valeur actuelle du champ beneficiaire
            var current_text = beneficiaire_field.find('option:selected').text();
            var ordre_virement_id = $('#id_ordre_virement_id').val();
            var is_new_ordre_virement = !ordre_virement_id;

            $.ajax({
                url: '/api/fournisseurs/get_beneficiaires/',
                data: { 
                    'type_ov': selected_type,
                    // N'appliquer le filtre des factures en attente qu'en création.
                    'filtre_factures_attente': is_new_ordre_virement ? 'true' : 'false'
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
                    } else if (should_preserve_value && current_text && current_text !== "---------") {
                        // En édition, conserver l'option courante même si l'API ne la renvoie pas.
                        beneficiaire_field.append(
                            $("<option></option>").attr("value", current_value).text(current_text)
                        );
                        beneficiaire_field.val(current_value);
                    }
                }
            });
        }

        type_ov_field.change(function() {
            update_beneficiaires();
        });

        // Ne pas écraser la valeur serveur en édition au chargement initial.
        if (!is_change_form) {
            update_beneficiaires();
        }
    });
})(django.jQuery);
