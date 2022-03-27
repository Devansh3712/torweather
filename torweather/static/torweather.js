function validate() {
    var email = document.forms["subscribe"]["email"].value;
    var fingerprint = document.forms["subscribe"]["fingerprint"].value;
    if (email == "") {
        alert("Email field cannot be empty.");
        return false;
    }
    if (fingerprint == "") {
        alert("Relay fingerprint field cannot be empty.")
        return false;
    }
    return true;
}

function toggleAll(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source)
            checkboxes[i].checked = source.checked;
    }
}
