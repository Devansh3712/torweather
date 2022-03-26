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
