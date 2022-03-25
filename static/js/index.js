
$(document).ready(function () {
    new WOW().init();
    wow = new WOW(
        {
            animateClass: 'animated',
            offset: 100,
        }
    );
    wow.init();
    console.log("outer")

    $(".searchIcon").click(() => {
        console.log("inner")
        $(".searchDiv").addClass("display");
    })

    function openNav() {
        document.getElementById("mySidenav").style.width = "250px";
        document.getElementById("main").style.display = "0";
        document.body.style.backgroundColor = "white";
    }

    function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
        document.getElementById("main").style.marginRight = "0";
        document.body.style.backgroundColor = "white";
    }



    $('#carouselExample').on('slide.bs.carousel', function (e) {


        var $e = $(e.relatedTarget);
        var idx = $e.index();
        var itemsPerSlide = 3;
        var totalItems = $('.carousel-item').length;

        if (idx >= totalItems - (itemsPerSlide - 1)) {
            var it = itemsPerSlide - (totalItems - idx);
            for (var i = 0; i < it; i++) {
                // append slides to end
                if (e.direction == "left") {
                    $('.carousel-item').eq(i).appendTo('.carousel-inner');
                }
                else {
                    $('.carousel-item').eq(0).appendTo('.carousel-inner');
                }
            }
        }
    });

    /* show lightbox when clicking a thumbnail */
    $('a.thumb').click(function (event) {
        event.preventDefault();
        var content = $('.modal-body');
        content.empty();
        var title = $(this).attr("title");
        $('.modal-title').html(title);
        content.html($(this).html());
        $(".modal-profile").modal({ show: true });
    });

    // bepartner.html page

    var current_fs, next_fs, previous_fs; //fieldsets
    var opacity;

    $(".next").click(function () {

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //Add Class Active
        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

        //show the next fieldset
        next_fs.show();
        //hide the current fieldset with style
        current_fs.animate({ opacity: 0 }, {
            step: function (now) {
                // for making fielset appear animation
                opacity = 1 - now;

                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                next_fs.css({ 'opacity': opacity });
            },
            duration: 600
        });
    });

    $(".previous").click(function () {

        current_fs = $(this).parent();
        previous_fs = $(this).parent().prev();

        //Remove class active
        $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

        //show the previous fieldset
        previous_fs.show();

        //hide the current fieldset with style
        current_fs.animate({ opacity: 0 }, {
            step: function (now) {
                // for making fielset appear animation
                opacity = 1 - now;

                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                previous_fs.css({ 'opacity': opacity });
            },
            duration: 600
        });
    });

    $('.radio-group .radio').click(function () {
        $(this).parent().find('.radio').removeClass('selected');
        $(this).addClass('selected');
    });

    $(".submit").click(function () {
        return false;
    })


    // refundproject.html page

    const slideValue = document.querySelector("span");
    const inputSlider = document.querySelector("input");
    inputSlider.oninput = (() => {
        let value = inputSlider.value;
        slideValue.textContent = value + "%";
        slideValue.style.right = (value) + "%";
        slideValue.classList.add("show");
    });


    // signin.html page

    let passwordInput = document.getElementById("txtPassword"),
        toggle = document.getElementById("btnToggle"),
        icon = document.getElementById("eyeIcon");

    function togglePassword() {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            icon.classList.add("fa-eye-slash");
        } else {
            passwordInput.type = "password";
            icon.classList.remove("fa-eye-slash");
        }
    }
    $(function () {
        var code = "+1"; // Assigning value from model.
        $('#txtPhone').val(code);
        $('#txtPhone').intlTelInput({
            autoHideDialCode: true,
            autoPlaceholder: "ON",
            dropdownContainer: document.body,
            formatOnDisplay: true,
            hiddenInput: "full_number",
            initialCountry: "auto",
            nationalMode: true,
            placeholderNumberType: "MOBILE",
            preferredCountries: ['US'],
            separateDialCode: true
        });
    });

    toggle.addEventListener("click", togglePassword, false);
    passwordInput.addEventListener("keyup", checkInput, false);

    $("#submit_form").click(function () {
        var passwordregex = /^(.{0,7}|[^0-9]*|[^A-Z]*|[a-zA-Z0-9]*)$/;
        var emailRegex = new RegExp(
            /^(("[\w-\s]+")|([\w-]+(?:\.[\w-]+)*)|("[\w-\s]+")([\w-]+(?:\.[\w-]+)*))(@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][0-9]\.|1[0-9]{2}\.|[0-9]{1,2}\.))((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){2}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\]?$)/i
        );
        var code = $("#txtPhone").intlTelInput("getSelectedCountryData").dialCode;
        var phoneNumber = $('#txtPhone').val();
        var name = $("#txtPhone").intlTelInput("getSelectedCountryData").name;
        alert('Country Code : ' + code + '\nPhone Number : ' + phoneNumber + '\nCountry Name : ' + name);
        var username = $.trim($("#username").val());
        var email = $.trim($("#email").val());
        var Password = $.trim($("#txtPassword").val());
        $("#username_error").html("");
        $("#txtPassword_error").html("");
        $("#email_error").html("");
        if (username == "") {
            $("#username").focus();
            $("#username_error").show();
            $("#username_error").html("Please Enter Username");
            return false;
        } else if (email == "") {
            $("#email").focus();
            $("#email_error").show();
            $("#email_error").html("Please Enter Email");
            return false;
        } else if (!email.match(emailRegex)) {
            $("#email").focus();
            $("#email_error").show();
            $("#email_error").html("Enter Valid Email");
            return false;
        } else if (Password == "") {
            $("#txtPassword").focus();
            $("#txtPassword_error").show();
            $("#txtPassword_error").html("Please Enter Password");
            return false;
        } else if (Password.match(passwordregex)) {
            $("#txtPassword-field").focus();
            $("#txtPassword_error").show();
            $("#txtPassword_error").html(
                "Make a strong password, 8 characters, including a uppercase letter, number and one special character."
            );
            return false;
        } else {
            alert("wefw");
        }
    });
});
