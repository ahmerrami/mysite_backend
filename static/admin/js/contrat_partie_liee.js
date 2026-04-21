// Affiche ou masque le champ date_accord_ca selon la valeur de partie_liee du client
// Fonctionne dans l'admin Django

function updateDateAccordCAField() {
    var clientSelect = document.getElementById('id_client');
    var dateAccordCAField = document.querySelector('.form-row.field-date_accord_ca, .form-group.field-date_accord_ca');
    if (!clientSelect || !dateAccordCAField) return;

    var clientId = clientSelect.value;
    if (!clientId) {
        dateAccordCAField.style.display = 'none';
        return;
    }

    // Récupérer via AJAX si le client est partie liée
    fetch('/admin/clients/client/' + clientId + '/change/?_to_field=id&_popup=1')
        .then(response => response.text())
        .then(html => {
            var partieLiee = html.includes('name="partie_liee" checked');
            dateAccordCAField.style.display = partieLiee ? '' : 'none';
        });
}

document.addEventListener('DOMContentLoaded', function() {
    updateDateAccordCAField();
    var clientSelect = document.getElementById('id_client');
    if (clientSelect) {
        clientSelect.addEventListener('change', updateDateAccordCAField);
    }
});