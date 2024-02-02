var sessionID = "davink32051";

$(document).ready(function () {
    if ((sessionID = getCookie("sessionID"))) document.getElementById("session").value = sessionID;
    storeValues();
});
