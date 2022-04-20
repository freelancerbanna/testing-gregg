function execDropdown (command, dropdown, tinyMCE)
{
    if ((tinyMCE != undefined) && (tinyMCE.activeEditor != undefined)) {
        var top = $('.splitElement').scrollTop();
        tinyMCE.activeEditor.focus();
        tinyMCE.activeEditor.execCommand(command, true, $(dropdown).find(':selected').text());
        $('.splitElement').scrollTop(top);
    }
}

function execDropdown (command, dropdown) {
    if ((tinyMCE != undefined) && (tinyMCE.activeEditor != undefined)) {
        var top = $('.splitElement').scrollTop();
        tinyMCE.activeEditor.focus();
        tinyMCE.activeEditor.execCommand(command, true, $(dropdown).find(':selected').text());
        $('.splitElement').scrollTop(top);
    }
}
    
$(document).ready(function(){
    window.allowNextForm = true;



    // Messages with the fader class fade out after 7 seconds
    if( $('.fader.messages').html() ){
        window.setTimeout(function(){
            $('.fader.messages').fadeOut(7000);
        }, 3000);
    }
    $('.icmo-show-next-hidden-row').click(function(e){
        e.preventDefault();
        $(this).parents('.icmo-hide-control').hide();
        $(this).parents('.icmo-hidden-row-parent')
            .find('.icmo-hidden-row').show();
    });
    
    $('#order-form-iframe').click(function(e){
        window.allowNextForm = true;
    });

    $('.icmo-form-next').click(function(e){
        e.preventDefault();
        if (window.allowNextForm) {
            $(this).parents('form').submit();
        }
        
    });
    $('.switch').on('gumby.onTrigger', function(){
            /* Someone  triggered a drawer switch. Issue a callback. */
            $(this).parents('.icmo-drawer').trigger('toggle-controls');
    });
    $('.icmo-drawer').on('toggle-controls', function(){
        $(this).find('.oda-drawer-switch').each(function(){
            if( $(this).is(":visible") ){
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });
    $('#plan-navigation-form').icmoPlanNavigationForm();
    $('#period-navigation-form').icmoPeriodNavigationForm();
    $('.font_selector').icmoFontSelector();
    $('.font_size_selector').icmoFontSizeSelector();
    if( $('.colorpicker-popup').length > 0 && typeof(tinyMCE) !== 'undefined' ){
    $('.colorpicker-popup').colorpicker({
        'closeOnOutside': false,
        'init': function(formatted, colorPicker){
            // STUB You'll want to put stuff here to update the color to the
            // color of the currently selected element...
            
            var color = '#'+$(this).val();
//            $(this).css({ 'background-color': color });
        },
        'close': function(formatted, colorPicker){
            var color = '#'+$(this).val();
            $(this).css({ 'background-color': color });
            // STUB color is now the selected color. Do stuff here...
            var widget = $(this).closest('.color_selector');
            if( $(widget).hasClass('cellcolor') ){
                // This widget modifies cell color...
                console.log('modifying cell color');
                if ((tinyMCE != undefined) && (tinyMCE.activeEditor != undefined)) {
                    tinyMCE.activeEditor.focus();
                    tinyMCE.activeEditor.execCommand('backcolor', false, color);
                }
            }else if( $(widget).hasClass('fontcolor') ){
                // This widget modifies font color...
                console.log('modifying font color');
                if ((tinyMCE != undefined) && (tinyMCE.activeEditor != undefined)) {
                    tinyMCE.activeEditor.focus();
                    tinyMCE.activeEditor.execCommand('forecolor', false, color);
                }
            }
        }
    });
    $('.color-icon').click(function(e){
            $(this).nextAll('.colorpicker-popup').click().focus();
            e.preventDefault();
    });
    }

    function execSingle (command)
    {
        if ((tinyMCE != undefined) && (tinyMCE.activeEditor != undefined)) {
            var top = $('.splitElement').scrollTop();
            tinyMCE.activeEditor.focus();
            tinyMCE.activeEditor.execCommand(command);
            $('.splitElement').scrollTop(top);
        }
    }

    $('.make-bold').click(function(){
        console.log('make text bold');
        execSingle('Bold');
    });
    $('.make-italic').click(function(){
        console.log('make text italic');
        execSingle('Italic');
    });
    $('.make-strikethrough').click(function(){
        console.log('make text strikethrough');
        execSingle('Strikethrough');
    });
});

(function($) {
    $.fn.icmoPlanNavigationForm = function() {
        var form = this;
        var page = false;
        if( $('#page_num').length > 0 ) page = $('#page_num').val();
        $(form).find('select').change(function(e){
            var id_array = $(this).val().split('-');
            var url_array = window.location.pathname.split('/');
            if( url_array[1] == 'user' ){
                url_array = ['', 'account', '0', 'plans', '0', 'revenue-goals'];
            }
            url_array[2] = id_array[0];
            url_array[4] = id_array[1];
            var get_array = window.location.search.substring(1).split('&');
            $.each(get_array, function(_i, v){
                if( typeof v !== 'undefined' ){
                    index = v.indexOf("page=");
                    if(index > -1) get_array.splice(get_array.indexOf(v), 1);
                    index = v.indexOf("action=");
                    if(index > -1) get_array.splice(get_array.indexOf(v), 1);
                }
            });
            var get_string = '?'+get_array.join('&');
            var url = url_array.join('/')+get_string;
            url += '&page='+id_array[2];
            window.location.href = url;
            e.preventDefault();
        });
    };
    $.fn.icmoPeriodNavigationForm = function() {
        var form = this;
        var time_label = $(this).find('select option:selected').text();
        $('.annual-sales-goal-label span').text(time_label);
        $('.segment-goal-label span').text(time_label);
        $(this).find('select').change(function(e){
            var time_div = $(this).val();
            var url = window.location.pathname;
            var get_args = location.search.replace('?', '').split('&');
            
            $.each(get_args, function(i, e){
                if( e.split('=')[0] && e.split('=')[0] =='d') 
                    get_args.splice(i, 1);
            });
            var new_url = url+'?'+get_args.join('&')+'&d='+time_div;
            
            window.location.href = new_url;
            e.preventDefault();
        });
    };
    $.fn.icmoFontSelector = function() {
        $(this).change(function(){
            console.log('Font selector changed');
            if( typeof(tinyMCE) !== 'undefined' ){
                execDropdown('FontName', this);
            }else{
                // There is nothing here. Control of this element is passed
                // to the budgets.js application instead.
            }
        });
    }
    $.fn.icmoFontSizeSelector = function() {
        $(this).change(function(){
             // STUB: Make this change the selected element!
            console.log('Font size selector changed');
            if( typeof(tinyMCE) !== 'undefined' ){
                execDropdown('FontName', this, tinyMCE);
            }else{
                // There is nothing here. Control of this element is passed
                // to the budgets.js application instead.
            }
        });
    }
}( jQuery ));
