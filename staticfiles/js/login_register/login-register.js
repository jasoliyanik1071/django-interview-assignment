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


    // login users
    $("#login_btn").on('click', function(event){
        event.preventDefault();
        debugger;
        // add_loader_in_page($('body'))
        var form = $(this).data('form-id');
        var data = $("#" + form).serialize();
        // var data = $(this).parent().siblings('form').serialize();
        // var data = $('#login_form').serialize();
        var current_url =  $(location).attr('href').split('?next=')[1];
        var page =  $(this).data('page');

        $('.login-error-message').empty();
        $('.login_input_error').remove();

        $('.register_input_error').remove();
        $('.error_message').remove();
        $(".register-error-message").html('');

        $.ajax({
            type: "POST",
            // url: $(this).data('url'),
            url: $(this).data("url") || "/loginsignup/login/",
            data: data,
            datatype: 'json',
            context: this,
            success: function(data){
                debugger;
                if (data.success){
                    // window.location.href = data.dashboard_url
                    if (page != undefined && page=='checkout') {
                        location.reload();
                    }
                    else if(current_url != undefined){
                        window.location.href = current_url
                    }
                    else{
                        window.location.href = data.dashboard_url
                    }
                }
                else{
                    debugger;

                    $('.login-error-message').empty();
                    $('.login_input_error').remove();
                    var field_errors = data.message;

                    $.each(field_errors, function( index, value ) {

                        console.log("index");
                        console.log(index);

                        $.each(value, function( i, error_list ) {

                            console.log(i);
                            console.log(error_list);

                            var error_field = $('#login_form input[name="' + index + '"]');

                            console.log(error_field);

                            if (error_field.length != 0) {
                                // Below condition for if signup modal open then only email & password error
                                // Shows only on signup page because it can shows on login page
                                debugger;
                                // if ($("#signup").is(':visible') && index == "email"){
                                
                                if ($(".common_login_register_modal").is(':visible') && index == "email"){
                                    var login_form = $('#login_form input[name="' + index + '"]').closest('form#login_form');
                                    var login_email = login_form.find($('#login_form input[name="' + index + '"]'));
                                    $(login_email).after("<span class='login_input_error'>"+error_list+"<span>");
                                }else{
                                    $('#login_form input[name="' + index + '"]').after("<span class='login_input_error'>"+error_list+"<span>");
                                    $('.login_input_error').css({'color': 'red'});
                                }

                            }
                            else {
                                var err_f = (index == "__all__") ? "Errors" : index;
                                $('.login-error-message').append("<p class='login_input_error error_message'>" + err_f + ": " + value + "<p>");
                                $('.login_input_error').css({'color': 'red'});
                            }
                        });

                    });

                    $('.login-error-message').css({'color': 'red'});
                    $('.login_input_error').css({'color': 'red'});

                    // // remove_loader_from_page();
                    // $('.login-error-message').empty();
                    // $.each(data.message, function( index, value ) {
                    //     $('.login-error-message').append("<p class='error_message'>"+value+"<p>");
                    // });
                }
            },
            error: function(data){
                debugger;
                $('.login-error-message').empty();
                $('.login_input_error').remove();

                console.log('Error');
                $.each(field_errors, function( index, value ) {

                    console.log("index");
                    console.log(index);

                    $.each(value, function( i, error_list ) {

                        console.log(i);
                        console.log(error_list);

                        var error_field = $('#login_form input[name="' + index + '"]');

                        console.log(error_field);

                        if (error_field.length != 0) {
                            // Below condition for if signup modal open then only email & password error
                            // Shows only on signup page because it can shows on login page
                            debugger;
                            // if ($("#signup").is(':visible') && index == "email"){
                            
                            if ($(".common_login_register_modal").is(':visible') && index == "email"){
                                var login_form = $('#login_form input[name="' + index + '"]').closest('form#login_form');
                                var login_email = login_form.find($('#login_form input[name="' + index + '"]'));
                                $(login_email).after("<span class='login_input_error'>"+error_list+"<span>");
                            }else{
                                $('#login_form input[name="' + index + '"]').after("<span class='login_input_error'>"+error_list+"<span>");
                                $('.login_input_error').css({'color': 'red'});
                            }

                        }
                        else {
                            var err_f = (index == "__all__") ? "Errors" : index;
                            $('.login-error-message').append("<p class='login_input_error error_message'>" + err_f + ": " + value + "<p>");
                            $('.login_input_error').css({'color': 'red'});
                        }
                    });
                });
                $('.login-error-message').css({'color': 'red'});
                $('.login_input_error').css({'color': 'red'});
                // remove_loader_from_page();
            }
        })

    });


    $('#register_btn').on('click', function(event){
        
        $('.login-error-message').empty();
        $('.login_input_error').remove();

        $('.register_input_error').remove();
        $('.error_message').remove();
        $(".register-error-message").html('');

        debugger;
        var data = $('#register_form').serialize();
        var is_agree = $("#register_form input[name='terms_conditions']").prop("checked");

        

        debugger
        console.log(is_agree);
        if (is_agree == true) {
            $.ajax({
                type: "POST",
                url: "/loginsignup/create/user/",
                data: data,
                datatype: "json",
                context: this,
                success: function(data){
                    debugger;
                    if (data.success){
                        // if (url == undefined) {
                        //     // $('#signup').modal('hide');
                        //     // $("#signup").css('z-index','9999999');
                        //     // $("#signup").modal('hide');
                        //     // $("#verify_with_otp_btn").attr('data-activation',"new");
                        //     // $("#resend_otp_btn").click();
                        //     // $("#signup").modal('hide');
                        //     set_up_popup_for_registration('new')
                        // }
                        // else {
                        //     window.location.href = data.soial_complete_url
                        // }
                        // window.location.href = data.dashboard_url
                        window.location.href = "/";
                        location.reload();
                    }
                    else{
                        debugger;
                        $('.register-error-message').empty();
                        $('.register_input_error').remove();
                        var field_errors = data.message;
                        $.each(field_errors, function( index, value ) {

                            console.log("index");
                            console.log(index);

                            $.each(value, function( i, error_list ) {

                                console.log(i);
                                console.log(error_list);

                                var error_field = $('#register_form input[name="' + index + '"]');

                                console.log(error_field);

                                if (error_field.length != 0) {
                                    // Below condition for if signup modal open then only email & password error
                                    // Shows only on signup page because it can shows on login page
                                    debugger;
                                    // if ($("#signup").is(':visible') && index == "email"){
                                    
                                    if ($(".common_login_register_modal").is(':visible') && index == "email"){
                                        var signup_form = $('#register_form input[name="' + index + '"]').closest('form#register_form');
                                        var signup_email = signup_form.find($('#register_form input[name="' + index + '"]'));
                                        $(signup_email).after("<span class='register_input_error'>"+error_list+"<span>");
                                    }else{
                                        $('#register_form input[name="' + index + '"]').after("<span class='register_input_error'>"+error_list+"<span>");
                                        $('.register_input_error').css({'color': 'red'});
                                    }

                                }
                                else {
                                    var err_f = (index == "__all__") ? "Errors" : index;
                                    $('.register-error-message').append("<p class='register_input_error error_message'>" + err_f + ": " + value + "<p>");
                                    $('.register_input_error').css({'color': 'red'});
                                }
                            });

                        });

                        $('.common_login_register_modal').css({'position': 'absolute'});
                    }
                },
                error: function(data){
                    console.log('Error');
                    $('.common_login_register_modal').css({'position': 'absolute'});
                }
            });
        }
        else {
            $('.register-error-message').empty();
            $('.register-error-message').append("<p class='register_input_error error_message'>Please agree to Terms & Conditions<p>");
        }


    });


});