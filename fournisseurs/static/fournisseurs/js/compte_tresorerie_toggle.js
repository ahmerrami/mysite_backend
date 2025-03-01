document.addEventListener("DOMContentLoaded", function () {
    function toggleFields() {
        let typeCompte = document.querySelector("#id_type_compte").value;

        // Sélection des champs avec leurs parents `.form-row`
        let banqueField = document.querySelector("#id_banque")?.closest(".form-row");
        let ribField = document.querySelector("#id_rib")?.closest(".form-row");
        let attestationField = document.querySelector("#id_attestation_rib_pdf")?.closest(".form-row");

        let nomCaisseField = document.querySelector("#id_nom_caisse")?.closest(".form-row");
        let emplacementField = document.querySelector("#id_emplacement_caisse")?.closest(".form-row");
        let detenteurField = document.querySelector("#id_detenteur_caisse")?.closest(".form-row");

        if (typeCompte === "bancaire") {
            // Afficher les champs bancaires
            banqueField && (banqueField.style.display = "flex");
            ribField && (ribField.style.display = "flex");
            attestationField && (attestationField.style.display = "flex");

            // Cacher les champs caisse
            nomCaisseField && (nomCaisseField.style.display = "none");
            emplacementField && (emplacementField.style.display = "none");
            detenteurField && (detenteurField.style.display = "none");
        } else {
            // Afficher les champs caisse
            nomCaisseField && (nomCaisseField.style.display = "flex");
            emplacementField && (emplacementField.style.display = "flex");
            detenteurField && (detenteurField.style.display = "flex");

            // Cacher les champs bancaires
            banqueField && (banqueField.style.display = "none");
            ribField && (ribField.style.display = "none");
            attestationField && (attestationField.style.display = "none");
        }
    }

    // Exécuter la fonction au chargement et écouter les changements
    let typeCompteField = document.querySelector("#id_type_compte");
    if (typeCompteField) {
        typeCompteField.addEventListener("change", toggleFields);
        toggleFields();  // Appliquer immédiatement pour cacher les champs inutiles au chargement
    }
});
