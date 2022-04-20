SignupJS = {};
var signupForm;
SignupJS.init = function (formSelector) {
    $signupForm = $(formSelector);

    SignupJS.registerValidation();
    SignupJS.registerWizard();
    SignupJS.registerSigPad();
    SignupJS.registerPaypalSubscribeButton();
    SignupJS.registerCouponListener();
    //SignupJS.registerPhoenix();
    SignupJS.registerPaymentFormToggles();

    SignupJS.numTabs = $signupForm.find('.tab-pane').length;

    // Init plan choice buttons
    $('.plan-select').on('click', function (e) {
        e.preventDefault();
        var plan_id = $(e.target).attr('data-plan-id');
        if (plan_id !== '') {
            SignupJS.activatePlan(plan_id);
        }
    });

    // Copy the user's title to the contract for convenience
    $signupForm.find('#id_title').on('change', function () {
        if ($signupForm.find('#id_signature-title').val() === '') {
            $signupForm.find('#id_signature-title').val($signupForm.find('#id_title').val());
            $signupForm.formValidation('revalidateField', 'signature-title');
        }
    });
};
SignupJS.updatePaymentSummary = function () {
    $('.paytable-loading').show();
    var code = $signupForm.find("input[name='code']").val();
    if (!code) {
        code = '';
    }
    var plan = $signupForm.find("input[name='plan']").val();
    if (!plan) {
        plan = '';
    }
    $.get(
        $signupForm.attr('data-summary-url'),
        "code=" + code + "&plan=" + plan,
        function (response) {
            $signupForm.find('.paytable_plan').html(response.plan_name);
            $signupForm.find('.paytable_interval').html(SignupJS.toTitleCase(response.plan_interval));
            $signupForm.find('.paytable_subfee').html(response.plan_subfee);
            $signupForm.find('.paytable_setupfee').html(response.plan_setupfee);
            if (response.plan_subfee_coupon_applied) {
                $signupForm.find('.paytable_subfee').addClass('text-success');
            } else {
                $signupForm.find('.paytable_subfee').removeClass('text-success');
            }
            if (response.plan_setupfee_coupon_applied) {
                $signupForm.find('.paytable_setupfee').addClass('text-success');
            } else {
                $signupForm.find('.paytable_setupfee').removeClass('text-success');
            }
            $('.paytable-loading').hide();
        }
    ).fail(function () {
            setTimeout(SignupJS.updatePaymentSummary, 1000);
        }
    )
};
SignupJS.activatePlan = function (plan_id) {
    if (!plan_id) {
        return false;
    }
    $('.plan-choice').removeClass("plan-selected").find('[role=button]').html('Select');
    $("input[name='plan']").val(plan_id);
    $('.' + plan_id).addClass("plan-selected").find('[role=button]').html('Selected');
    SignupJS.updatePaymentSummary();
};

SignupJS.registerValidation = function () {
    $signupForm.formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        excluded: ':disabled',
        fields: {
            cardNumber: {
                selector: '#cardNumber',
                validators: {
                    notEmpty: {},
                    callback: {
                        callback: StripeForm.validateCardNumber,
                        message: "Please specify a valid credit card number."
                    }
                }
            },
            cardExpiry: {
                selector: '#cardExpiry',
                validators: {
                    notEmpty: {},
                    callback: {
                        callback: StripeForm.validateCardExpiry,
                        message: "Invalid expiration date."
                    }
                }
            },
            cardCVC: {
                selector: '#cardCVC',
                validators: {
                    notEmpty: {},
                    callback: {
                        callback: StripeForm.validateCardCVC,
                        message: "Invalid CVC."
                    }
                }
            }
        }
    }).on('success.form.fv', function (e) {
        e.preventDefault();
        // The default form submission is through stripe, so call stripe
        StripeForm.payWithStripe(e, function () {
            // Clear client side stored form data
            if (typeof SignupJS.$fieldsToStore !== 'undefined') {
                SignupJS.$fieldsToStore.phoenix('remove');
            }
            // Submit the form
            $signupForm.get(0).submit();
        })
    });
};

SignupJS.registerSigPad = function () {
    SignupJS.sigPadAPI = $signupForm.signaturePad({
        lineTop: 80,
        validateFields: false,
        output: '.sigOutput',
        name: '.sigName',
        drawOnly: true,
        onFormError: function () {
            var $sigFormGroup = $('#div_id_signature-signature_json');
            if ($('.sigOutput').val() !== '') {
                $sigFormGroup.removeClass("has-error").addClass('has-success');
            } else {
                $sigFormGroup.removeClass("has-success").addClass('has-error');
            }
        }
    });

};

SignupJS.registerWizard = function () {
    SignupJS.wizard = $signupForm.bootstrapWizard({
        onTabClick: function (tab, navigation, index) {
            return false;
        },
        nextSelector: '.wizard-next',
        previousSelector: '.wizard-prev',
        onNext: function (tab, navigation, index) {
            return SignupJS.validateTab(index - 1);
        },
        onPrevious: function (tab, navigation, index) {
            return true;
        },
        onTabShow: function (tab, navigation, index) {
            SignupJS.toggleWizardButtons(index);
            $('#_last_tab').val(index);
        }
    });
};

SignupJS.registerPhoenix = function () {
    // Save some of the fields to users local storage for convenience, and restore on page load
    SignupJS.$fieldsToStore = $signupForm.find("input[name][name!='csrfmiddlewaretoken'][data-phoenix-exclude!='true'],select[data-phoenix-exclude!='true']");

    // Restore the last tab worked on and show a welcome back message
    $('#_last_tab').on('phnx.loaded', function () {
        var $wbAlert = $('#welcome_back_alert');
        $wbAlert.show().fadeTo(5000, .3).slideUp(250, function () {
            $wbAlert.alert('close');
        });
        var lasttab = $('#_last_tab').val();
        if (lasttab) {
            lasttab = Math.min(lasttab, 4);
            $signupForm.bootstrapWizard('show', lasttab);
        }
    });
    // The two functions below will also restore the state of the plan summary
    // Restore the state of the plan selector
    $("input[name='plan']").on('phnx.loaded', function (e) {
        SignupJS.activatePlan($(e.target).val());
    });

    // Ensure non-empty fields are revalidated
    $("input").on('phnx.loaded', function (e) {
        if ($(e.target).val()) {
            $signupForm.formValidation('revalidateField', $(e.target).attr('name'));
            if ($(e.target).attr('name') === 'code') {
                $('.div_id_code').show();
            }
        }

    });
    SignupJS.$fieldsToStore.phoenix({
        saveInterval: 1000
    });
    // Sync all windows viewing this form together
    SignupJS.phoenixEnabled = true;

    $(window).on('storage', function (event) {
        SignupJS.$fieldsToStore.phoenix('stop');
        SignupJS.phoenixEnabled = false;
    });
    $(window).focus(function () {
        if (SignupJS.phoenixEnabled === false) {
            SignupJS.$fieldsToStore.phoenix('load');
            SignupJS.$fieldsToStore.phoenix('start');
            SignupJS.phoenixEnabled = true;
        }
    })
};

SignupJS.registerPaypalSubscribeButton = function () {
    $signupForm.find('#paypal_subscribe_button').click(function (e) {
        $signupForm.find('#paypal_subscribe_button').html('Connecting to Paypal <i class="fa fa-spinner fa-pulse"></i>').prop('disabled', true);
        var target_url = $(e.target).attr('data-target-url');
        var source_url = $(e.target).attr('data-source-url');
        var plan_slug = $('input[name="plan"]').val();
        var get_auth_url_url = $(e.target).attr('data-paypal-get-auth-url');
        var url = get_auth_url_url + "?target_url=" + target_url + "&source_url=" + source_url + "&plan_slug=" + plan_slug;
        $.post(
            url,
            $signupForm.serialize(),
            function (data) {
                if (data.paypal_auth_url) {
                    // Clear client side stored form data
                    if (typeof SignupJS.$fieldsToStore !== 'undefined') {
                        SignupJS.$fieldsToStore.phoenix('remove');
                    }
                    location.href = data.paypal_auth_url;
                } else {
                    SignupJS.paypalSubscribeButtonFailed();
                }
            }
        ).fail(function () {
                SignupJS.paypalSubscribeButtonFailed();
            })
    })

};

SignupJS.paypalSubscribeButtonFailed = function () {
    $signupForm.find('#paypal_subscribe_button').html('Subscribe by PayPal ACH').prop('disabled', false);
    bootbox.alert("Failed to connect to paypal, please try again.");
};

SignupJS.registerCouponListener = function () {
    // Admin code link toggle
    $('a.admin_code').click(function (e) {
        e.preventDefault();
        $('.div_id_code').toggle();
    });
    $signupForm.formValidation().on('err.validator.fv', function (e, data) {
        if (data.field === 'code') {
            $('#coupon_success').remove();
            SignupJS.updatePaymentSummary();
        }
    });
    $signupForm.formValidation().on('success.validator.fv', function (e, data) {
        if (data.field === 'code') {
            if (data.element.val() === '') {
                var $parent = data.element.parents('.form-group');

                // Remove the has-success class
                $parent.removeClass('has-success');

                // Hide the success icon
                data.element.data('fv.icon').hide();
            }
            if (data.validator === 'remote') {
                if (data.result.success_message) {
                    $(data.element).after("<span class='text-success' id='coupon_success'>" + data.result.success_message + "</span>");
                } else {
                    $('#coupon_success').remove();
                }
                SignupJS.updatePaymentSummary();
            }
        }
    });
};

SignupJS.registerPaymentFormToggles = function (e) {
    $signupForm.find('input.payment-selector').on('ifChanged', function (e) {
        if ($signupForm.find('input.payment-selector:checked').val() === 'credit_card') {
            $signupForm.find('.credit-card-form-body').collapse('show');
            $signupForm.find('.paypal-form-body').collapse('hide');
        } else {
            $signupForm.find('.paypal-form-body').collapse('show');
            $signupForm.find('.credit-card-form-body').collapse('hide');
        }
    })
};

SignupJS.validateTab = function (index) {
    var fv = $signupForm.data('formValidation'); // FormValidation instance
    var $tab = $signupForm.find('.tab-pane').eq(index);

    // Validate the container
    fv.validateContainer($tab);

    var isValidStep = fv.isValidContainer($tab);
    // Force a subscription plan to be chosen
    if ($tab.find('input[name="plan"]').length && $tab.find('input[name="plan"]').val() === '') {
        isValidStep = false;
        bootbox.alert("Please choose a subscription to continue.");
    }

    // Force signature validation
    if ($tab.find('input[name="signature-signature_json"]').length) {
        isValidStep = SignupJS.sigPadAPI.validateForm();
        $('#id_signature-signature_uri_b64').val(SignupJS.sigPadAPI.getSignatureImage())
    }
    if (isValidStep) {
        $.post($signupForm.attr('data-store-form-url'), $signupForm.serialize());
    }

    return !(isValidStep === false || isValidStep === null);
};

SignupJS.toggleWizardButtons = function (index) {
    if (index === SignupJS.numTabs - 1) {
        $('.wizard-next').hide();
    } else {
        $('.wizard-next').show();
    }
    if (index === 0) {
        $('.wizard-prev').hide();
    } else {
        $('.wizard-prev').show();
    }
};

SignupJS.toTitleCase = function (str) {
    return str.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
};