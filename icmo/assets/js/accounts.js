$(document).ready(function(){
    $('.delete-company-link').click(function(e){
        /* Feeds company information to the delete form so that it can be
         * handled correctly */
         
        var row = $(this).parents('.row');
        var company_name = $(row).find('.company-name a').html();
        var cid = $(row).find('.company-name a').attr('id').split('_')[1];
        var modal = $('#delete-company-modal');
        var modal_title = $('#delete-company-modal .modal-title :header')
                                .text().split(' ')[0]+' '+company_name;
                                
        $('#delete-company-modal .modal-title :header').text(modal_title);
        $('#delete-company-modal #id_cid').val(cid);
        e.preventDefault();
    });
    $('.clone-company-link').click(function(e){
        /* Feeds company information to the clone form so that it can be
         * handled correctly */
         
        var row = $(this).parents('.row');
        var company_name = $(row).find('.company-name a').html();
        var cid = $(row).find('.company-name a').attr('id').split('_')[1];
        var modal = $('#clone-company-modal');
        var modal_title = $('#clone-company-modal .modal-title :header')
                                .text().split(' ')[0]+' '+company_name;
                                
        $('#clone-company-modal .modal-title :header').text(modal_title);
        $('#clone-company-modal #id_name').val(company_name+' (copy)')
        $('#clone-company-modal #id_t').val(cid);
        e.preventDefault();
    });
    $('form#update-contact-form').icmoUpdateContactForm();
    $('form#update-my-user-form').icmoUpdateMyUserForm();
    $('.remove-user-link').click(function(e){
        /* Feeds user information to the remove form so that it can be
         * handled correctly */
         
        var row = $(this).parents('.row');
        var user_name = $(row).find('.user-name').html();
        var uid = $(row).find('.user-name').attr('id').split('_')[1];
        var modal = $('#remove-user-modal');
        var modal_title = $('#remove-user-modal .modal-title :header')
                                .text().split(' ')[0]+' '+user_name;
                                
        $('#remove-user-modal .modal-title :header').text(modal_title);
        $('#remove-user-modal #id_uid').val(uid);
        e.preventDefault();
    });
    $('.recycle-link').click(function(e){
        /* Feeds recycle information to the dialog */
         
        var row = $(this).closest('.row');
        var asset_name = $(row).find('.asset-name').html();
        var a = $(row).attr('id').split('_');
        var atype = a[0];
        var aid = a[1];
        var modal = $('#recycle-modal');
        var modal_title = $('#recycle-modal .modal-title :header')
                                .text().split(' ')[0]+' '+asset_name;
                                
        $('#recycle-modal .modal-title :header').text(modal_title);
        $('#recycle-modal #id_aid').val(aid);
        $('#recycle-modal #id_atype').val(atype);
        e.preventDefault();
    });
    $('.icmo-faq').icmoFaq();
});

(function($) {
    $.fn.icmoUpdateContactForm = function() {
        var form = this;
        $('.save-contact-details').click(function(e){
            $(form).submit();
            e.preventDefault();
        });
    };
    $.fn.icmoUpdateMyUserForm = function() {
        var form = this;
        $('.save-my-user-details').click(function(e){
            $(form).submit();
            e.preventDefault();
        });
    };
    $.fn.icmoFaq = function() {
        $(this).find('h1').each(function(){
            var content = $(this).text();
            $(this).html('<a href="#"><i class="fa fa-caret-right"></i> '+content+'</a>');
        });
        $(this).find('h1 a').each(function(){
            $(this).click(function(e){
                var caret = $(this).find('i').first();
                if( $(caret).hasClass('fa-caret-right') ){
                    $(caret).removeClass('fa-caret-right').addClass('fa-caret-down');
                }else{
                    $(caret).removeClass('fa-caret-down').addClass('fa-caret-right');
                }
                $(this).closest('h1').nextUntil('h1').toggle();
                e.preventDefault();
            });
        });
    };
}( jQuery ));
