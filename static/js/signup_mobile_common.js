$(document).ready(function(event){

    var current_url = $(location).attr('href');
    if (current_url.includes('signup')){
        setTimeout(function(){
            // $(".number .social-register").click();
            $('.login-link .signUp').click();
        },500);
    }
    else if (current_url.includes('?next=')){
        setTimeout(function(){
            $(".login-link .loginBtn").click();
        },500);
    }

    var input = document.querySelector("#id_phone_number");
    // jQuery
    
    // Restrict to remove Country code from Register modal    START
    $("#id_phone_number").on("blur keyup change", function() {
        if($(this).val() == '') {
            var getCode = $("#id_phone_number").intlTelInput('getSelectedCountryData').dialCode;
            $(this).val('+'+getCode);
        }
    });

    var get_phone_number_ids = ["#id_phone_number_for_link_app_section","#id_phone_number"]

    $(document).on("click",".country",function(){
        get_phone_number_ids.forEach(function(element){
            if($(element).val() == '') {
            var getCode = $(element).intlTelInput('getSelectedCountryData').dialCode;
            $(element).val('+'+getCode);
            }
        })
        $('#get_link_btn_app_section').parents('form').find('#error-msg').addClass('hide');
        $("#id_phone_number_for_link_app_section").css('border','1px solid #ccc');
        $('#get_link_btn_app_section').parents('form').find('#error-msg').text('');
        $("#id_phone_number_for_link_app_section").val('+'+$("#id_phone_number_for_link_app_section").intlTelInput('getSelectedCountryData').dialCode);
        
    });
    // Restrict to remove Country code from Register modal    END

    $("#id_phone_number").intlTelInput({
        initialCountry: "in",
        preferredCountries: ["in"],
      // options here
    });
    if (window.location.pathname.includes('reset_password_confirm')){
        $('#forgot-pwd-confirm').modal('show');
    }


    // Restrict to remove Country code from get link    START
    $("#id_phone_number_for_link_app_section").on("blur keyup change", function() {
        if($(this).val() == '') {
            var getCode = $(this).intlTelInput('getSelectedCountryData').dialCode;
            $(this).val('+'+getCode);
        }
    });

    // Restrict to remove Country code from get link    END

    // $("#id_phone_number_for_link_banner").intlTelInput({
    //     initialCountry: "in",
    //     preferredCountries: ["in"],
    //     // options here
    // });

    $("#id_phone_number_for_link_app_section").intlTelInput({
        initialCountry: "in",
        preferredCountries: ["in"],
        // options here
    });

    if($('#id_phone_number_for_link_app_section').val() == '') {
        var getCode = $('#id_phone_number_for_link_app_section').intlTelInput('getSelectedCountryData').dialCode;
        if(getCode != 'undefined'){
            $('#id_phone_number_for_link_app_section').val('+'+getCode);
        }
    }

});