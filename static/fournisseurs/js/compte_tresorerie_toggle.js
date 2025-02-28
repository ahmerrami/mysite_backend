document.addEventListener("DOMContentLoaded", function () {
    function toggleFields() {
        let typeCompte = document.querySelector("#id_type_compte").value;

        // Sélection des champs
        let banqueField = document.querySelector(".form-row.field-banque");
        let ribField = document.querySelector(".form-row.field-rib");
        let attestationField = document.querySelector(".form-row.field-attestation_rib_pdf");

        let nomCaisseField = document.querySelector(".form-row.field-nom_caisse");
        let emplacementField = document.querySelector(".form-row.field-emplacement_caisse");
        let detenteurField = document.querySelector(".form-row.field-detenteur_caisse");

        if (typeCompte === "bancaire") {
            banqueField.style.display = "block";
            ribField.style.display = "block";
            attestationField.style.display = "block";

            nomCaisseField.style.display = "none";
            emplacementField.style.display = "none";
            detenteurField.style.display = "none";
        } else {
            banqueField.style.display = "none";
            ribField.style.display = "none";
            attestationField.style.display = "none";

            nomCaisseField.style.display = "block";
            emplacementField.style.display = "block";
            detenteurField.style.display = "block";
        }
    }

    // Appliquer la fonction lors du chargement et sur changement de type_compte
    let typeCompteField = document.querySelector("#id_type_compte");
    if (typeCompteField) {
        typeCompteField.addEventListener("change", toggleFields);
        toggleFields();  // Exécuter au chargement
    }
});
