$( document ).ready(function() {

    //apply js for pending activation
    window.addEventListener("load", function(){
        $("#id_phone_number").intlTelInput({
            initialCountry: "in",
            preferredCountries: ["in"],
            separateDialCode: true
        });
    })


    $("#id_phone_number").on("keypress", function(evt){

        // restricting user to enter more than 15 characters
        if($(this).val().length>15)
            return false;

        var iKeyCode = (evt.which) ? evt.which : evt.keyCode
        if (iKeyCode != 46 && iKeyCode > 31 && (iKeyCode < 48 || iKeyCode > 57))
            return false;

        return true;
    })


});