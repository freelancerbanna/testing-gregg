/*
 The MIT License (MIT)

 Copyright (c) 2015 William Hilton

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
 */

/* If you're using Stripe for payments */
var StripeForm = {};
StripeForm.init = function ($form, PublishableKey) {
    StripeForm.$form = $form;
    Stripe.setPublishableKey(PublishableKey);
    /* Fancy restrictive input formatting via jQuery.payment library*/
    StripeForm.$form.find('input[id=cardNumber]').payment('formatCardNumber');
    StripeForm.$form.find('input[id=cardCVC]').payment('formatCardCVC');
    StripeForm.$form.find('input[id=cardExpiry]').payment('formatCardExpiry');

};

StripeForm.payWithStripe = function (e, successCallback) {
    e.preventDefault();

    /* Visual feedback */
    StripeForm.$form.find('[type=submit]').html('Validating <i class="fa fa-spinner fa-pulse"></i>').prop('disabled', true);

    /* Create token */
    var expiry = StripeForm.$form.find('[id=cardExpiry]').payment('cardExpiryVal');
    var ccData = {
        number: StripeForm.$form.find('[id=cardNumber]').val().replace(/\s/g, ''),
        cvc: StripeForm.$form.find('[id=cardCVC]').val(),
        exp_month: expiry.month,
        exp_year: expiry.year
    };

    Stripe.card.createToken(ccData, function stripeResponseHandler(status, response) {
        if (response.error) {
            /* Visual feedback */
            StripeForm.$form.find('[type=submit]').html('Try again').prop('disabled', false);
            /* Show Stripe errors on the form */
            StripeForm.$form.find('.payment-errors').text(response.error.message);
            StripeForm.$form.find('.payment-errors').closest('.row').show();
        } else {
            /* Visual feedback */
            /* Hide Stripe errors on the form */
            StripeForm.$form.find('.payment-errors').closest('.row').hide();
            StripeForm.$form.find('.payment-errors').text("");
            // response contains id and card, which contains additional card details
            StripeForm.$form.find('input[name=stripe_token]').val(response.id);
            StripeForm.$form.find('input[name=stripe_last4]').val(response.card.last4);
            StripeForm.$form.find('input[name=stripe_brand]').val(response.card.brand);
            successCallback();
        }
    });
};


/* Form validation using Stripe client-side validation helpers */
StripeForm.validateCardNumber = function (value, validator, $field) {
    return Stripe.card.validateCardNumber(value);
};
StripeForm.validateCardExpiry = function (value, validator, $field) {
    value = $.payment.cardExpiryVal(value);
    return Stripe.card.validateExpiry(value.month, value.year);
};
StripeForm.validateCVC = function (value, validator, $field) {
    return Stripe.card.validateCVC(value);
};